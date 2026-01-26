import sys
import logging

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PySide6.QtCore import Slot, QSettings

# these must be absolute imports for PyInstaller
from race_results.ui.main_window import Ui_main_window
from race_results.config import config_dialog
from race_results.executive import ResultsFileWatcher

_logger = logging.getLogger()

_start_text = "Start Service"
_stop_text = "Stop Service"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        _settings_location = str((Path.home() / "race-results.ini").resolve())
        self.settings = QSettings(_settings_location, QSettings.Format.IniFormat)

        OrgSlug = str(self.settings.value("OrgSlug", defaultValue=""))
        ApiKey = str(self.settings.value("ApiKey", defaultValue=""))
        ResultsPath = Path(str(self.settings.value("ResultsPath", defaultValue="")))
        AutoStart = bool(
            self.settings.value("AutoStart", defaultValue=False, type=bool)
        )

        self.config_dlg = config_dialog(
            self,
            org_slug=OrgSlug,
            api_key=ApiKey,
            results_fpath=str(ResultsPath.resolve()),
            autostart=AutoStart,
        )

        self.watch_worker = ResultsFileWatcher(self, self.settings)
        self.watch_worker.started.connect(self.watcher_started)
        self.watch_worker.finished.connect(self.watcher_stopped)
        self.watch_worker.status_update.connect(self.ui.statusbar.showMessage)

        if AutoStart:
            if self.start_watcher():
                self.watcher_started()

    @Slot()
    def modify_config(self):
        self.config_dlg.open()
        self.config_dlg.finished.connect(self.update_config)

    @Slot(int)
    def update_config(self, result):
        if result != QDialog.DialogCode.Accepted:
            return

        org_slug = self.config_dlg.OrgSlug
        api_key = self.config_dlg.ApiKey
        results_path = self.config_dlg.ResultsPath

        self.settings.setValue("OrgSlug", org_slug)
        self.settings.setValue("ApiKey", api_key)
        self.settings.setValue("ResultsPath", results_path)
        self.settings.setValue("AutoStart", self.config_dlg.AutoStart)
        self.settings.sync()

    @Slot()
    def toggle_service(self):
        if not self.watch_worker.isRunning() and self.watch_worker.CanRun:
            self.start_watcher()

        elif self.watch_worker.isRunning():
            self.watch_worker.requestInterruption()

        self.ui.button_service.setEnabled(False)

    @Slot()
    def force_update(self):
        if self.watch_worker.isRunning():
            self.watch_worker.force_update = True

    def start_watcher(self) -> bool:
        if self.watch_worker.isRunning():
            _logger.error("Worker thread is already running")
            return False

        if not self.watch_worker.CanRun:
            _logger.error("Unable to start watch service due to invalid configuration")
            return False

        self.watch_worker.start()
        return True

    def watcher_stopped(self):
        self.ui.button_config.setEnabled(True)
        self.ui.button_forceupdate.setEnabled(False)
        self.ui.button_service.setEnabled(True)
        self.ui.button_service.setText(_start_text)
        self.ui.statusbar.showMessage("Worker thread stopped")

    def watcher_started(self):
        self.ui.button_config.setEnabled(False)
        self.ui.button_forceupdate.setEnabled(True)
        self.ui.button_service.setEnabled(True)
        self.ui.button_service.setText(_stop_text)
        self.ui.statusbar.showMessage("Worker thread running...")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
