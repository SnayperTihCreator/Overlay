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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QSizePolicy,
    QSpacerItem, QTreeWidget, QTreeWidgetItem, QWidget)

class Ui_Setting(object):
    def setupUi(self, Setting):
        if not Setting.objectName():
            Setting.setObjectName(u"Setting")
        Setting.resize(724, 347)
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

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.frame = QFrame(Setting)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(400, 0))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pageCommon = QWidget(self.frame)
        self.pageCommon.setObjectName(u"pageCommon")

        self.horizontalLayout_2.addWidget(self.pageCommon)

        self.pageWebSockets = QWidget(self.frame)
        self.pageWebSockets.setObjectName(u"pageWebSockets")
        self.horizontalLayout_3 = QHBoxLayout(self.pageWebSockets)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.formLayout.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.activateLabel = QLabel(self.pageWebSockets)
        self.activateLabel.setObjectName(u"activateLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.activateLabel)

        self.pws_activateCheckBox = QCheckBox(self.pageWebSockets)
        self.pws_activateCheckBox.setObjectName(u"pws_activateCheckBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pws_activateCheckBox)


        self.horizontalLayout_3.addLayout(self.formLayout)


        self.horizontalLayout_2.addWidget(self.pageWebSockets)


        self.horizontalLayout.addWidget(self.frame)


        self.retranslateUi(Setting)

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

        self.activateLabel.setText(QCoreApplication.translate("Setting", u"Activate", None))
    # retranslateUi

