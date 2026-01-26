# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget)

class Ui_config_dialog(object):
    def setupUi(self, config_dialog):
        if not config_dialog.objectName():
            config_dialog.setObjectName(u"config_dialog")
        config_dialog.resize(330, 156)
        config_dialog.setModal(True)
        self.formLayout = QFormLayout(config_dialog)
        self.formLayout.setObjectName(u"formLayout")
        self.label_org = QLabel(config_dialog)
        self.label_org.setObjectName(u"label_org")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_org)

        self.text_org = QLineEdit(config_dialog)
        self.text_org.setObjectName(u"text_org")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.text_org)

        self.label_api = QLabel(config_dialog)
        self.label_api.setObjectName(u"label_api")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_api)

        self.text_api = QLineEdit(config_dialog)
        self.text_api.setObjectName(u"text_api")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.text_api)

        self.label_resultsfile = QLabel(config_dialog)
        self.label_resultsfile.setObjectName(u"label_resultsfile")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_resultsfile)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.text_resultsfile = QLineEdit(config_dialog)
        self.text_resultsfile.setObjectName(u"text_resultsfile")

        self.horizontalLayout.addWidget(self.text_resultsfile)

        self.button_resultsfile = QPushButton(config_dialog)
        self.button_resultsfile.setObjectName(u"button_resultsfile")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.button_resultsfile.setIcon(icon)

        self.horizontalLayout.addWidget(self.button_resultsfile)


        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(config_dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setCenterButtons(True)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.buttonBox)

        self.cb_autostart = QCheckBox(config_dialog)
        self.cb_autostart.setObjectName(u"cb_autostart")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.cb_autostart)


        self.retranslateUi(config_dialog)
        self.buttonBox.accepted.connect(config_dialog.accept)
        self.buttonBox.rejected.connect(config_dialog.reject)
        self.button_resultsfile.clicked.connect(config_dialog.browse_results_file)

        QMetaObject.connectSlotsByName(config_dialog)
    # setupUi

    def retranslateUi(self, config_dialog):
        config_dialog.setWindowTitle(QCoreApplication.translate("config_dialog", u"Dialog", None))
        self.label_org.setText(QCoreApplication.translate("config_dialog", u"Organization Slug", None))
        self.label_api.setText(QCoreApplication.translate("config_dialog", u"API Key", None))
        self.label_resultsfile.setText(QCoreApplication.translate("config_dialog", u"Live Results Path", None))
        self.button_resultsfile.setText("")
        self.cb_autostart.setText(QCoreApplication.translate("config_dialog", u"Automatically start upload service on startup", None))
    # retranslateUi

