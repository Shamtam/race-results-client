# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_main_window(object):
    def setupUi(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName(u"main_window")
        main_window.resize(350, 189)
        main_window.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        main_window.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_lastupdate = QLabel(self.centralwidget)
        self.label_lastupdate.setObjectName(u"label_lastupdate")

        self.gridLayout.addWidget(self.label_lastupdate, 2, 0, 1, 1)

        self.button_forceupdate = QPushButton(self.centralwidget)
        self.button_forceupdate.setObjectName(u"button_forceupdate")
        self.button_forceupdate.setEnabled(False)

        self.gridLayout.addWidget(self.button_forceupdate, 5, 0, 1, 2)

        self.label_event = QLabel(self.centralwidget)
        self.label_event.setObjectName(u"label_event")

        self.gridLayout.addWidget(self.label_event, 1, 0, 1, 1)

        self.label_org = QLabel(self.centralwidget)
        self.label_org.setObjectName(u"label_org")

        self.gridLayout.addWidget(self.label_org, 0, 0, 1, 1)

        self.text_org = QLabel(self.centralwidget)
        self.text_org.setObjectName(u"text_org")

        self.gridLayout.addWidget(self.text_org, 0, 1, 1, 1)

        self.button_service = QPushButton(self.centralwidget)
        self.button_service.setObjectName(u"button_service")

        self.gridLayout.addWidget(self.button_service, 4, 0, 1, 2)

        self.text_event = QLabel(self.centralwidget)
        self.text_event.setObjectName(u"text_event")

        self.gridLayout.addWidget(self.text_event, 1, 1, 1, 1)

        self.text_lastupdate = QLabel(self.centralwidget)
        self.text_lastupdate.setObjectName(u"text_lastupdate")

        self.gridLayout.addWidget(self.text_lastupdate, 2, 1, 1, 1)

        self.button_config = QPushButton(self.centralwidget)
        self.button_config.setObjectName(u"button_config")

        self.gridLayout.addWidget(self.button_config, 6, 0, 1, 2)

        self.gridLayout.setColumnStretch(1, 1)
        main_window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName(u"statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)
        self.button_config.clicked.connect(main_window.modify_config)
        self.button_forceupdate.clicked.connect(main_window.force_update)
        self.button_service.clicked.connect(main_window.toggle_service)

        QMetaObject.connectSlotsByName(main_window)
    # setupUi

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(QCoreApplication.translate("main_window", u"Race Results", None))
        self.label_lastupdate.setText(QCoreApplication.translate("main_window", u"Last Update:", None))
        self.button_forceupdate.setText(QCoreApplication.translate("main_window", u"Force Update", None))
        self.label_event.setText(QCoreApplication.translate("main_window", u"Event:", None))
        self.label_org.setText(QCoreApplication.translate("main_window", u"Organization:", None))
        self.text_org.setText(QCoreApplication.translate("main_window", u"orgName", None))
        self.button_service.setText(QCoreApplication.translate("main_window", u"Start Service", None))
        self.text_event.setText(QCoreApplication.translate("main_window", u"event#", None))
        self.text_lastupdate.setText(QCoreApplication.translate("main_window", u"timestamp", None))
        self.button_config.setText(QCoreApplication.translate("main_window", u"Configuration", None))
    # retranslateUi

