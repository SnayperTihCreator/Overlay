# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialogSettingsTemplate.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinimumSize)
        self.labelNamePlugin = QLabel(Form)
        self.labelNamePlugin.setObjectName(u"labelNamePlugin")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelNamePlugin.sizePolicy().hasHeightForWidth())
        self.labelNamePlugin.setSizePolicy(sizePolicy)
        self.labelNamePlugin.setMinimumSize(QSize(0, 40))
        self.labelNamePlugin.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelNamePlugin)

        self.btnOpenFolderPlugin = QPushButton(Form)
        self.btnOpenFolderPlugin.setObjectName(u"btnOpenFolderPlugin")

        self.verticalLayout_3.addWidget(self.btnOpenFolderPlugin)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.spinBox = QSpinBox(Form)
        self.spinBox.setObjectName(u"spinBox")

        self.horizontalLayout.addWidget(self.spinBox)

        self.spinBox_2 = QSpinBox(Form)
        self.spinBox_2.setObjectName(u"spinBox_2")

        self.horizontalLayout.addWidget(self.spinBox_2)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.formLayout)


        self.verticalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(Form)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.labelNamePlugin.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.btnOpenFolderPlugin.setText(QCoreApplication.translate("Form", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443 \u043f\u043b\u0430\u0433\u0438\u043d\u0430", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u041f\u043e\u0437\u0438\u0446\u0438\u044f", None))
    # retranslateUi

