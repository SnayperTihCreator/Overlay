# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialogSettings.ui'
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
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(435, 300)
        font = QFont()
        font.setFamilies(["Segoe UI"])
        Form.setFont(font)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.boxMain = QVBoxLayout()
        self.boxMain.setObjectName("boxMain")
        self.labelPlugin = QLabel(Form)
        self.labelPlugin.setObjectName("labelPlugin")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelPlugin.sizePolicy().hasHeightForWidth())
        self.labelPlugin.setSizePolicy(sizePolicy)
        self.labelPlugin.setMaximumSize(QSize(16777215, 50))
        self.labelPlugin.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.boxMain.addWidget(self.labelPlugin)

        self.btnOpenFolderPlugin = QPushButton(Form)
        self.btnOpenFolderPlugin.setObjectName("btnOpenFolderPlugin")

        self.boxMain.addWidget(self.btnOpenFolderPlugin)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.coordinatesLabel = QLabel(Form)
        self.coordinatesLabel.setObjectName("coordinatesLabel")
        self.coordinatesLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.coordinatesLabel
        )

        self.coordinatesWidget = QWidget(Form)
        self.coordinatesWidget.setObjectName("coordinatesWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.coordinatesWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.coordinatesWidgetX = QSpinBox(self.coordinatesWidget)
        self.coordinatesWidgetX.setObjectName("coordinatesWidgetX")
        self.coordinatesWidgetX.setMaximum(65536)

        self.horizontalLayout_3.addWidget(self.coordinatesWidgetX)

        self.coordinatesWidgetY = QSpinBox(self.coordinatesWidget)
        self.coordinatesWidgetY.setObjectName("coordinatesWidgetY")
        self.coordinatesWidgetY.setMaximum(65536)

        self.horizontalLayout_3.addWidget(self.coordinatesWidgetY)

        self.formLayout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.coordinatesWidget
        )

        self.positionLabel = QLabel(Form)
        self.positionLabel.setObjectName("positionLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.positionLabel)

        self.transparencySpinBox = QSpinBox(Form)
        self.transparencySpinBox.setObjectName("transparencySpinBox")
        self.transparencySpinBox.setMaximum(100)

        self.formLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.transparencySpinBox
        )

        self.transparencyLabel = QLabel(Form)
        self.transparencyLabel.setObjectName("transparencyLabel")

        self.formLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.transparencyLabel
        )

        self.positionBox = QComboBox(Form)
        self.positionBox.addItem("")
        self.positionBox.addItem("")
        self.positionBox.addItem("")
        self.positionBox.setObjectName("positionBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.positionBox)

        self.horizontalLayout.addLayout(self.formLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.mobilityBox = QCheckBox(Form)
        self.mobilityBox.setObjectName("mobilityBox")

        self.verticalLayout.addWidget(self.mobilityBox)

        self.clickabilityBox = QCheckBox(Form)
        self.clickabilityBox.setObjectName("clickabilityBox")

        self.verticalLayout.addWidget(self.clickabilityBox)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.boxMain.addLayout(self.horizontalLayout)

        self.verticalLayout_2.addLayout(self.boxMain)

        self.buttonBox = QDialogButtonBox(Form)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.labelPlugin.setText(QCoreApplication.translate("Form", "TextLabel", None))
        self.btnOpenFolderPlugin.setText(
            QCoreApplication.translate(
                "Form",
                "\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0430\u043f\u043a\u0443 \u043f\u043b\u0430\u0433\u0438\u043d\u0430",
                None,
            )
        )
        self.coordinatesLabel.setText(
            QCoreApplication.translate("Form", "Coordinates", None)
        )
        self.positionLabel.setText(QCoreApplication.translate("Form", "Position", None))
        self.transparencySpinBox.setSuffix(
            QCoreApplication.translate("Form", "%", None)
        )
        self.transparencyLabel.setText(
            QCoreApplication.translate("Form", "Transparency", None)
        )
        self.positionBox.setItemText(
            0,
            QCoreApplication.translate(
                "Form",
                "\u0412\u0441\u0435\u0433\u0434\u0430 \u043f\u043e\u0437\u0430\u0434\u0438 \u043e\u043a\u043e\u043d",
                None,
            ),
        )
        self.positionBox.setItemText(
            1,
            QCoreApplication.translate(
                "Form", "\u041d\u043e\u0440\u043c\u0430\u043b\u044c\u043d\u043e", None
            ),
        )
        self.positionBox.setItemText(
            2,
            QCoreApplication.translate(
                "Form",
                "\u0412\u0441\u0435\u0433\u0434\u0430 \u043f\u043e\u0432\u0435\u0440\u0445 \u043e\u043a\u043d\u043e",
                None,
            ),
        )

        self.mobilityBox.setText(
            QCoreApplication.translate(
                "Form",
                "\u041f\u043e\u0434\u0432\u0438\u0436\u043d\u043e\u0441\u0442\u044c",
                None,
            )
        )
        self.clickabilityBox.setText(
            QCoreApplication.translate(
                "Form",
                "\u041d\u0435 \u043a\u043b\u0438\u043a\u0430\u0431\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c",
                None,
            )
        )

    # retranslateUi
