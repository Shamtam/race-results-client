import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QWidget

from .ui.console_dialog import Ui_Dialog
from .log import TextEditLogHandler


class ConsoleDialog(QDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.handler = TextEditLogHandler(self.ui.textEdit)

        self.change_level(self.ui.comboBox.currentIndex())

    def close(self) -> bool:
        self.rejected.emit()
        return super().close()

    @Slot(int)
    def change_level(self, level_idx: int):
        logging.getLogger().setLevel(10 + level_idx * 10)

    @property
    def Handler(self) -> logging.Handler:
        return self.handler
