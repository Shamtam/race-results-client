# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'console_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(600, 400)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textEdit = QTextEdit(Dialog)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEdit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_clear = QPushButton(Dialog)
        self.button_clear.setObjectName(u"button_clear")

        self.horizontalLayout.addWidget(self.button_clear)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.comboBox = QComboBox(Dialog)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)
        self.comboBox.currentIndexChanged.connect(Dialog.change_level)
        self.button_clear.clicked.connect(self.textEdit.clear)

        self.comboBox.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Console", None))
        self.button_clear.setText(QCoreApplication.translate("Dialog", u"Clear Console", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Dialog", u"Debug", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Dialog", u"Info", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Dialog", u"Warning", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("Dialog", u"Error", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("Dialog", u"Critical", None))

        self.comboBox.setCurrentText(QCoreApplication.translate("Dialog", u"Info", None))
    # retranslateUi

