import sys
import logging

from pathlib import Path

from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QCloseEvent, QHideEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)

# these must be absolute imports for PyInstaller
from race_results.ui.main_window import Ui_main_window
from race_results.config import ConfigDialog
from race_results.console import ConsoleDialog
from race_results.executive import ResultsFileWatcher
from race_results.settings import SettingsStore
from race_results.log import StatusBarLogHandler

_logger = logging.getLogger()
_worker_logger = logging.getLogger("executive")


class MainWindow(QMainWindow):

    set_force_update_flag = Signal()
    set_close_event_flag = Signal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)

        self.settings = SettingsStore()

        ApiKey = self.settings.ApiKey
        ResultsPath = str(Path(self.settings.ResultsPath).resolve())
        AutoStart = self.settings.AutoStart
        TrayStart = self.settings.TrayStart

        self.config_dlg = ConfigDialog(
            self,
            api_key=ApiKey,
            results_fpath=ResultsPath,
            autostart=AutoStart,
            traystart=TrayStart,
        )

        self.console_dlg = ConsoleDialog(self)
        _logger.addHandler(self.console_dlg.Handler)
        _logger.addHandler(StatusBarLogHandler(self.ui.statusbar))

        self.watch_worker = ResultsFileWatcher(self, self.settings)

        # setup tray icon
        self.tray_menu = QMenu(parent=self)
        self.tray_menu.addActions(
            [
                self.ui.actionConnect,
                self.ui.actionDisconnect,
            ]
        )
        self.tray_menu.addSeparator()
        self.tray_menu.addActions(
            [
                self.ui.actionForceUpdate,
                self.ui.actionCloseEvent,
            ]
        )
        self.tray_menu.addSeparator()
        self.tray_menu.addActions(
            [
                self.ui.actionConsole,
                self.ui.actionQuit,
            ]
        )
        self.tray = QSystemTrayIcon(self.windowIcon())
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

        # setup actions
        self.ui.actionForceUpdate.triggered.connect(self.force_update)
        self.ui.actionConfigure.triggered.connect(self.modify_config)
        self.ui.actionConsole.toggled.connect(self.console_dlg.setVisible)

        # setup signals/slots
        self.watch_worker.started.connect(self.watcher_started)
        self.watch_worker.connected.connect(self.connected)
        self.watch_worker.finished.connect(self.disconnected)
        self.watch_worker.log_message.connect(self.process_worker_log)
        self.watch_worker.notification.connect(self.notify)
        self.set_close_event_flag.connect(self.watch_worker.queue_event_close)
        self.set_force_update_flag.connect(self.watch_worker.queue_force_update)
        self.config_dlg.finished.connect(self.update_config)
        self.console_dlg.rejected.connect(self.ui.actionConsole.toggle)
        self.tray.activated.connect(self.process_tray)

        if AutoStart:
            self.connect()
        else:
            self.disconnected(notify=False)

        if TrayStart:
            self.setVisible(False)
        else:
            self.showNormal()
            self.activateWindow()

    @Slot()
    def modify_config(self):
        self.config_dlg.open()

    @Slot()
    def close_event(self):
        self.set_close_event_flag.emit()

    @Slot()
    def force_update(self):
        self.set_force_update_flag.emit()

    @Slot(int)
    def update_config(self, result):
        if result != QDialog.DialogCode.Accepted:
            return

        self.settings.clear()

        self.settings.setValue("ApiKey", self.config_dlg.ApiKey)
        self.settings.setValue("ResultsPath", self.config_dlg.ResultsPath)
        self.settings.setValue("AutoStart", self.config_dlg.AutoStart)
        self.settings.setValue("TrayStart", self.config_dlg.TrayStart)

        self.settings.sync()

    @Slot()
    def connect(self):
        if not self.watch_worker.isRunning() and self.watch_worker.CanRun:
            self.start_watcher()

    @Slot()
    def disconnect(self):
        if self.watch_worker.isRunning():
            self.watch_worker.requestInterruption()

            for elem in (
                self.ui.actionDisconnect,
                self.ui.actionForceUpdate,
                self.ui.actionCloseEvent,
            ):
                elem.setEnabled(False)

    @Slot(str, str)
    def connected(self, org: str, event: str):
        self.ui.text_org.setText(org)
        self.ui.text_event.setText(event)
        self.ui.actionConnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(True)

        for elem in (
            self.ui.actionDisconnect,
            self.ui.actionForceUpdate,
            self.ui.actionCloseEvent,
        ):
            elem.setEnabled(True)

        _logger.info("Service successfully started")
        self.ui.text_status.setText("Connected to server, watching live results file")
        self.notify("Connected to server")

    @Slot()
    def disconnected(self, notify=True):
        _logger.info("Service stopped")

        self.watch_worker.wait()
        self.ui.actionConfigure.setEnabled(True)
        self.ui.actionForceUpdate.setEnabled(False)
        self.ui.actionConnect.setVisible(True)
        self.ui.actionConnect.setEnabled(True)
        self.ui.actionDisconnect.setVisible(False)

        self.ui.text_org.setText("")
        self.ui.text_event.setText("")
        self.ui.text_status.setText("Service not running.")

        if notify:
            self.notify("Disconnected from server")

    @Slot(int, str)
    def process_worker_log(self, loglvl: int, msg: str):
        _worker_logger.log(loglvl, msg)

    @Slot(QSystemTrayIcon.ActivationReason)
    def process_tray(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    @Slot(str)
    def notify(self, msg: str):
        self.tray.showMessage(self.windowTitle(), msg)

    def hideEvent(self, event: QHideEvent) -> None:
        self.setVisible(False)
        event.ignore()

    def closeEvent(self, event: QCloseEvent) -> None:
        result = QMessageBox.question(
            self,
            "Confirm exit",
            "Are you sure you want to exit?",
        )

        if result == QMessageBox.StandardButton.Yes:
            self.disconnect()
            self.watch_worker.wait()
            QApplication.quit()
        else:
            event.ignore()

    def start_watcher(self):
        if self.watch_worker.isRunning():
            _logger.error("Worker thread is already running")

        if not self.watch_worker.CanRun:
            _logger.error("Missing API Key or Invalid Results File")

        self.watch_worker.start()

    def watcher_started(self):
        _logger.debug("Worker thread launched...")
        self.ui.text_status.setText("Authenticating with server...")
        self.ui.actionConnect.setEnabled(False)
        self.ui.actionConfigure.setEnabled(False)


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
