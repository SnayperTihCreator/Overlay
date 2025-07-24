# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

from Service.ModelData import PluginList

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btnStopOverlay = QPushButton(self.centralwidget)
        self.btnStopOverlay.setObjectName(u"btnStopOverlay")
        self.btnStopOverlay.setGeometry(QRect(270, 310, 75, 24))
        self.btnHide = QPushButton(self.centralwidget)
        self.btnHide.setObjectName(u"btnHide")
        self.btnHide.setGeometry(QRect(310, 210, 75, 24))
        self.btnSetting = QPushButton(self.centralwidget)
        self.btnSetting.setObjectName(u"btnSetting")
        self.btnSetting.setGeometry(QRect(350, 490, 75, 23))
        self.widgetListPlugin = QWidget(self.centralwidget)
        self.widgetListPlugin.setObjectName(u"widgetListPlugin")
        self.widgetListPlugin.setGeometry(QRect(190, 30, 450, 450))
        self.widgetListPlugin.setMinimumSize(QSize(450, 450))
        self.verticalLayout = QVBoxLayout(self.widgetListPlugin)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listPlugins = PluginList(self.widgetListPlugin)
        self.listPlugins.setObjectName(u"listPlugins")
        self.listPlugins.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.verticalLayout.addWidget(self.listPlugins)

        self.btnListUpdate = QPushButton(self.widgetListPlugin)
        self.btnListUpdate.setObjectName(u"btnListUpdate")

        self.verticalLayout.addWidget(self.btnListUpdate)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Overlay", None))
        self.btnStopOverlay.setText(QCoreApplication.translate("MainWindow", u"ESC", None))
        self.btnHide.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.btnSetting.setText("")
        self.btnListUpdate.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u0441\u043f\u0438\u0441\u043e\u043a", None))
    # retranslateUi

