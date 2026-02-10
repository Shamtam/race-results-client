from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QDialog, QFileDialog

from .ui.config_dialog import Ui_config_dialog
from .defaults import default_host


class ConfigDialog(QDialog):

    def __init__(
        self,
        parent: QMainWindow,
        api_key: str = "",
        results_fpath: str = "",
        autostart: bool = False,
        traystart: bool = False,
    ):
        super().__init__(parent, modal=True)
        self.ui = Ui_config_dialog()
        self.ui.setupUi(self)

        # pre-populate dialog
        for val, ui_elem in (
            (api_key, self.ui.text_api),
            (results_fpath, self.ui.text_resultsfile),
        ):
            if val:
                ui_elem.setText(val)

        self.ui.cb_autostart.setChecked(autostart)
        self.ui.cb_traystart.setChecked(traystart)

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
    def ResultsPath(self) -> str:
        return self.ui.text_resultsfile.text()

    @property
    def AutoStart(self) -> bool:
        return self.ui.cb_autostart.isChecked()

    @property
    def TrayStart(self) -> bool:
        return self.ui.cb_traystart.isChecked()
