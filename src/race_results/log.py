import logging

from PySide6.QtWidgets import QTextEdit, QStatusBar


class TextEditLogHandler(logging.Handler):

    def __init__(self, textbox: QTextEdit):
        super().__init__()
        self.textbox = textbox
        self.textbox.document().setMaximumBlockCount(1000)

        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] {%(module)s}: %(message)s", "%H:%M:%S"
        )
        self.setFormatter(self.formatter)

    def emit(self, record: logging.LogRecord) -> None:

        color_map = {
            logging.DEBUG: "#acacac",
            logging.INFO: "#000000",
            logging.WARNING: "#ff7b00",
            logging.ERROR: "#ad0000",
            logging.CRITICAL: "#8900a5",
        }

        self.textbox.setTextColor(color_map[record.levelno])
        self.textbox.append(self.format(record))

        # only auto-scroll if near end of log
        sb = self.textbox.verticalScrollBar()
        if (sb.maximum() - sb.sliderPosition()) < 20:
            self.textbox.ensureCursorVisible()


class StatusBarLogHandler(logging.Handler):

    def __init__(self, statusbar: QStatusBar):
        super().__init__()
        self.statusbar = statusbar

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno < logging.INFO:
            return

        msg = (
            record.message
            if record.levelno < logging.ERROR
            else "*** ERROR: See console for details ***"
        )
        self.statusbar.showMessage(
            msg, timeout=(30000 if record.levelno < logging.WARNING else None)
        )
