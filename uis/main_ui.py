# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        font = QFont()
        font.setFamilies(["Segoe UI"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listPlugins = QListWidget(self.centralwidget)
        self.listPlugins.setObjectName("listPlugins")
        self.listPlugins.setGeometry(QRect(9, 9, 300, 400))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPlugins.sizePolicy().hasHeightForWidth())
        self.listPlugins.setSizePolicy(sizePolicy)
        self.listPlugins.setMinimumSize(QSize(300, 400))
        self.listPlugins.setMaximumSize(QSize(200, 400))
        self.btnStopOverlay = QPushButton(self.centralwidget)
        self.btnStopOverlay.setObjectName("btnStopOverlay")
        self.btnStopOverlay.setGeometry(QRect(270, 310, 75, 24))
        self.btnHide = QPushButton(self.centralwidget)
        self.btnHide.setObjectName("btnHide")
        self.btnHide.setGeometry(QRect(310, 210, 75, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Overlay", None)
        )
        self.btnStopOverlay.setText(
            QCoreApplication.translate("MainWindow", "ESC", None)
        )
        self.btnHide.setText(QCoreApplication.translate("MainWindow", "X", None))

    # retranslateUi
