# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QSizePolicy,
    QSpacerItem, QStackedWidget, QTreeWidget, QTreeWidgetItem,
    QWidget)

class Ui_Setting(object):
    def setupUi(self, Setting):
        if not Setting.objectName():
            Setting.setObjectName(u"Setting")
        Setting.resize(656, 347)
        self.horizontalLayout = QHBoxLayout(Setting)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.treeWidget = QTreeWidget(Setting)
        QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(self.treeWidget)
        self.treeWidget.setObjectName(u"treeWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.treeWidget)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.stackedWidget = QStackedWidget(Setting)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setMinimumSize(QSize(350, 0))
        self.pageCommon = QWidget()
        self.pageCommon.setObjectName(u"pageCommon")
        self.stackedWidget.addWidget(self.pageCommon)
        self.pageWebSocket = QWidget()
        self.pageWebSocket.setObjectName(u"pageWebSocket")
        self.stackedWidget.addWidget(self.pageWebSocket)

        self.horizontalLayout.addWidget(self.stackedWidget)


        self.retranslateUi(Setting)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Setting)
    # setupUi

    def retranslateUi(self, Setting):
        Setting.setWindowTitle(QCoreApplication.translate("Setting", u"Setting", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Setting", u"Settings", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Setting", u"Common", None));
        ___qtreewidgetitem2 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("Setting", u"WebSockets", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

    # retranslateUi

