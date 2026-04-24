import sys
import logging

from typing import Any

from PySide6.QtCore import QEvent, Qt, QUrl, Signal, Slot, QSharedMemory
from PySide6.QtGui import QCloseEvent, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)

# these must be absolute imports for PyInstaller
from race_results.config import ConfigDialog
from race_results.console import ConsoleDialog
from race_results.defaults import default_app_guid, default_log_fpath, help_permalink
from race_results.executive import ResultsFileWatcher
from race_results.log import FileLogHandler, StatusBarLogHandler
from race_results.settings import SettingsStore
from race_results.ui.main_window import Ui_main_window

_logger = logging.getLogger()
_worker_logger = logging.getLogger("executive")


class MainWindow(QMainWindow):

    set_force_update_flag = Signal()
    set_close_event_flag = Signal()
    set_current_event = Signal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)

        self.settings = SettingsStore()

        AutoStart = self.settings.AutoStart
        StartMinimized = self.settings.StartMinimized
        LogToFile = self.settings.LogToFile

        self.config_dlg = ConfigDialog(self, self.settings)

        self.console_dlg = ConsoleDialog(self)
        _logger.addHandler(self.console_dlg.Handler)
        _logger.addHandler(StatusBarLogHandler(self.ui.statusbar))

        if LogToFile:
            _logger.addHandler(FileLogHandler(default_log_fpath))

        self.watch_worker = ResultsFileWatcher(self, self.settings)

        # setup tray
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

        # sync to system theme at startup before showing tray icon
        self.process_theme_change()

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
        self.set_current_event.connect(self.watch_worker.set_current_event)
        self.config_dlg.finished.connect(self.update_config)
        self.console_dlg.rejected.connect(self.ui.actionConsole.toggle)
        self.tray.activated.connect(self.process_tray)

        if AutoStart:
            self.connect()
        else:
            self.disconnected(notify=False)

        if StartMinimized:
            self.showMinimized()
        else:
            self.showNormal()
            self.activateWindow()

    def event(self, event: QEvent) -> bool:

        super().event(event)

        # handle system-wide theme change at runtime
        if event.type() == event.Type.ThemeChange:
            self.process_theme_change()

        return True

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

        # retain hidden host setting if it exists
        host = self.settings.value("Host", None)

        # rebuild settings store from scratch using dialog values
        self.settings.clear()

        self.settings.setValue("ApiKey", self.config_dlg.ApiKey)
        self.settings.setValue("ResultsPath", self.config_dlg.ResultsPath)
        self.settings.setValue("HeatsPath", self.config_dlg.HeatsPath)
        self.settings.setValue("AutoStart", self.config_dlg.AutoStart)
        self.settings.setValue("StartMinimized", self.config_dlg.StartMinimized)
        self.settings.setValue("LogToFile", self.config_dlg.LogToFile)

        if host is not None:
            self.settings.setValue("Host", host)

        # write settings to disk
        self.settings.sync()

        # update file logging if necessary
        file_handlers = list(
            filter(lambda x: isinstance(x, FileLogHandler), _logger.handlers)
        )
        if self.settings.LogToFile and not file_handlers:
            _logger.addHandler(FileLogHandler(default_log_fpath))
        elif not self.settings.LogToFile and file_handlers:
            for h in file_handlers:
                _logger.removeHandler(h)

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

    @Slot(dict)
    def connected(self, state: dict[str, Any]):
        all_events = state["events"]
        event_names = [x["name"] for x in all_events]

        # determine event and send to worker thread if necessary
        if len(event_names) > 1:
            name, ok = QInputDialog.getItem(
                self,
                "Event Selection",
                "Choose current event",
                event_names,
                0,
                False,
            )

            # event selected
            if ok and name:
                idx = event_names.index(name)
                event = all_events[idx]
                self.set_current_event.emit(event)

            # selection aborted or invalid, kill worker thread
            else:
                self.disconnect()
                return

        # only one event, worker thread already set current event
        else:
            event = all_events[0]

        self.ui.text_org.setText(state["org"]["name"])
        self.ui.text_event.setText(event["name"])
        self.ui.actionConnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(True)

        for elem in (
            self.ui.actionDisconnect,
            self.ui.actionForceUpdate,
            self.ui.actionCloseEvent,
        ):
            elem.setEnabled(True)

        self.setWindowIcon(self.icon_connected)
        self.tray.setIcon(self.icon_connected)

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

        self.setWindowIcon(self.icon_normal)
        self.tray.setIcon(self.icon_normal)

        if notify:
            self.notify("Disconnected from server")

    @Slot(int, str)
    def process_worker_log(self, loglvl: int, msg: str):
        _worker_logger.log(loglvl, msg)

        # pop up notification for warnings/errors
        if loglvl >= logging.WARNING:
            self.notify(msg)

    @Slot(QSystemTrayIcon.ActivationReason)
    def process_tray(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    @Slot(str)
    def notify(self, msg: str):
        self.tray.showMessage(self.windowTitle(), msg)

    @Slot()
    def show_help(self):
        QDesktopServices.openUrl(QUrl(help_permalink))

    def process_theme_change(self):
        suffix = (
            "light"
            if app.styleHints().colorScheme() == Qt.ColorScheme.Light
            else "dark"
        )
        self.icon_normal = QIcon(f":/icons/logo_{suffix}.ico")
        self.icon_connected = QIcon(f":/icons/connected_{suffix}.ico")

        current_icon = (
            self.icon_connected if self.watch_worker.isRunning() else self.icon_normal
        )
        self.setWindowIcon(current_icon)
        self.tray.setIcon(current_icon)

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
m = QSharedMemory(default_app_guid)

if not m.create(1):
    dlg = QMessageBox.warning(
        None,
        "Race-Results already running",
        "Another instance of Race Results is already running",
    )
    sys.exit(-1)
else:
    window = MainWindow()
    sys.exit(app.exec())
