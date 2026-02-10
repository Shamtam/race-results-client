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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QMainWindow,
    QSizePolicy, QStatusBar, QToolBar, QWidget)
from . import resource_rc

class Ui_main_window(object):
    def setupUi(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName(u"main_window")
        main_window.resize(450, 160)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(sizePolicy)
        main_window.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        icon = QIcon()
        icon.addFile(u":/icons/emoji_u1f3c1.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        main_window.setWindowIcon(icon)
        main_window.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        main_window.setDocumentMode(False)
        main_window.setUnifiedTitleAndToolBarOnMac(True)
        self.actionForceUpdate = QAction(main_window)
        self.actionForceUpdate.setObjectName(u"actionForceUpdate")
        self.actionForceUpdate.setEnabled(False)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SyncSynchronizing))
        self.actionForceUpdate.setIcon(icon1)
        self.actionForceUpdate.setMenuRole(QAction.MenuRole.NoRole)
        self.actionCloseEvent = QAction(main_window)
        self.actionCloseEvent.setObjectName(u"actionCloseEvent")
        self.actionCloseEvent.setEnabled(False)
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.actionCloseEvent.setIcon(icon2)
        self.actionCloseEvent.setMenuRole(QAction.MenuRole.NoRole)
        self.actionConfigure = QAction(main_window)
        self.actionConfigure.setObjectName(u"actionConfigure")
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.actionConfigure.setIcon(icon3)
        self.actionConfigure.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.actionConnect = QAction(main_window)
        self.actionConnect.setObjectName(u"actionConnect")
        self.actionConnect.setChecked(False)
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemShutdown))
        self.actionConnect.setIcon(icon4)
        self.actionConnect.setMenuRole(QAction.MenuRole.NoRole)
        self.actionConsole = QAction(main_window)
        self.actionConsole.setObjectName(u"actionConsole")
        self.actionConsole.setCheckable(True)
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DialogInformation))
        self.actionConsole.setIcon(icon5)
        self.actionConsole.setMenuRole(QAction.MenuRole.NoRole)
        self.actionDisconnect = QAction(main_window)
        self.actionDisconnect.setObjectName(u"actionDisconnect")
        self.actionDisconnect.setEnabled(False)
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkOffline))
        self.actionDisconnect.setIcon(icon6)
        self.actionDisconnect.setMenuRole(QAction.MenuRole.NoRole)
        self.actionQuit = QAction(main_window)
        self.actionQuit.setObjectName(u"actionQuit")
        icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.actionQuit.setIcon(icon7)
        self.actionQuit.setMenuRole(QAction.MenuRole.QuitRole)
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.formLayout = QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(u"formLayout")
        self.label_org = QLabel(self.centralwidget)
        self.label_org.setObjectName(u"label_org")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_org.sizePolicy().hasHeightForWidth())
        self.label_org.setSizePolicy(sizePolicy1)
        self.label_org.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_org)

        self.text_org = QLabel(self.centralwidget)
        self.text_org.setObjectName(u"text_org")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.text_org)

        self.label_event = QLabel(self.centralwidget)
        self.label_event.setObjectName(u"label_event")
        sizePolicy1.setHeightForWidth(self.label_event.sizePolicy().hasHeightForWidth())
        self.label_event.setSizePolicy(sizePolicy1)
        self.label_event.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_event)

        self.text_event = QLabel(self.centralwidget)
        self.text_event.setObjectName(u"text_event")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.text_event)

        self.label_status = QLabel(self.centralwidget)
        self.label_status.setObjectName(u"label_status")
        sizePolicy1.setHeightForWidth(self.label_status.sizePolicy().hasHeightForWidth())
        self.label_status.setSizePolicy(sizePolicy1)
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_status)

        self.text_status = QLabel(self.centralwidget)
        self.text_status.setObjectName(u"text_status")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.text_status)

        main_window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setSizeGripEnabled(False)
        main_window.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(main_window)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionConnect)
        self.toolBar.addAction(self.actionDisconnect)
        self.toolBar.addAction(self.actionForceUpdate)
        self.toolBar.addAction(self.actionCloseEvent)
        self.toolBar.addAction(self.actionConfigure)
        self.toolBar.addAction(self.actionConsole)

        self.retranslateUi(main_window)
        self.actionCloseEvent.triggered.connect(main_window.close_event)
        self.actionConfigure.triggered.connect(main_window.modify_config)
        self.actionForceUpdate.triggered.connect(main_window.force_update)
        self.actionConnect.triggered.connect(main_window.connect)
        self.actionDisconnect.triggered.connect(main_window.disconnect)
        self.actionQuit.triggered.connect(main_window.close)

        QMetaObject.connectSlotsByName(main_window)
    # setupUi

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(QCoreApplication.translate("main_window", u"Race Results", None))
        self.actionForceUpdate.setText(QCoreApplication.translate("main_window", u"Force Update", None))
        self.actionCloseEvent.setText(QCoreApplication.translate("main_window", u"Close Event", None))
        self.actionConfigure.setText(QCoreApplication.translate("main_window", u"Configure", None))
        self.actionConnect.setText(QCoreApplication.translate("main_window", u"Connect", None))
#if QT_CONFIG(statustip)
        self.actionConnect.setStatusTip(QCoreApplication.translate("main_window", u"Connect to Server", None))
#endif // QT_CONFIG(statustip)
        self.actionConsole.setText(QCoreApplication.translate("main_window", u"Console", None))
        self.actionDisconnect.setText(QCoreApplication.translate("main_window", u"Disconnect", None))
        self.actionQuit.setText(QCoreApplication.translate("main_window", u"Quit", None))
        self.label_org.setText(QCoreApplication.translate("main_window", u"Organization:", None))
        self.text_org.setText("")
        self.label_event.setText(QCoreApplication.translate("main_window", u"Event:", None))
        self.text_event.setText("")
        self.label_status.setText(QCoreApplication.translate("main_window", u"Status:", None))
        self.text_status.setText("")
        self.toolBar.setWindowTitle(QCoreApplication.translate("main_window", u"toolBar", None))
    # retranslateUi

