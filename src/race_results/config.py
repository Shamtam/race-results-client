from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QDialog, QFileDialog

from .ui.config_dialog import Ui_config_dialog
from .settings import SettingsStore


class ConfigDialog(QDialog):

    def __init__(self, parent: QMainWindow, settings: SettingsStore):
        super().__init__(parent, modal=True)
        self.ui = Ui_config_dialog()
        self.ui.setupUi(self)

        # pre-populate dialog
        for val, ui_elem in (
            (settings.ApiKey, self.ui.text_api),
            (settings.ResultsPath, self.ui.text_resultsfile),
            (settings.HeatsPath, self.ui.text_heatsfile),
        ):
            if val:
                ui_elem.setText(val)

        for val, ui_elem in (
            (settings.AutoStart, self.ui.cb_autostart),
            (settings.TrayStart, self.ui.cb_traystart),
            (settings.LogToFile, self.ui.cb_logfile),
        ):
            ui_elem.setChecked(val)

    @Slot()
    def browse_heats_file(self):
        fpath, result = QFileDialog.getOpenFileName(
            self,
            "Choose AxWare Heat Assignments Text File",
            options=(
                QFileDialog.Option.ReadOnly
                | QFileDialog.Option.HideNameFilterDetails
                | QFileDialog.Option.DontUseCustomDirectoryIcons
            ),
            filter="AxWare Heat Assignment Text Files (*.txt)",
        )

        if fpath is not None:
            self.ui.text_heatsfile.setText(fpath)

    @Slot()
    def browse_results_file(self):
        fpath, result = QFileDialog.getOpenFileName(
            self,
            "Choose AxWare Live Results File",
            options=(
                QFileDialog.Option.ReadOnly
                | QFileDialog.Option.HideNameFilterDetails
                | QFileDialog.Option.DontUseCustomDirectoryIcons
            ),
            filter="AxWare Live Results Files (*.htm)",
        )

        if fpath is not None:
            self.ui.text_resultsfile.setText(fpath)

    @property
    def ApiKey(self) -> str:
        return self.ui.text_api.text()

    @property
    def AutoStart(self) -> bool:
        return self.ui.cb_autostart.isChecked()

    @property
    def HeatsPath(self) -> str:
        return self.ui.text_heatsfile.text()

    @property
    def LogToFile(self) -> bool:
        return self.ui.cb_logfile.isChecked()

    @property
    def ResultsPath(self) -> str:
        return self.ui.text_resultsfile.text()

    @property
    def TrayStart(self) -> bool:
        return self.ui.cb_traystart.isChecked()
