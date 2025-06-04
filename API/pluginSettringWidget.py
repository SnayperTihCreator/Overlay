import os
from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from box import Box

from uis.dialogSettings_ui import Ui_Form
from utils import getAppPath, open_file_manager
from .OverlayWidget import OverlayWidget
from .config import Config


class PluginSettingsWidget(OverlayWidget, Ui_Form):
    def __init__(self, window, name_plugin, parent=None):
        super().__init__(Config(__file__, "overlay_widget", "settings", False), parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.confirming)
        self.buttonBox.rejected.connect(self.canceling)

        self.win = window

        self.labelPlugin.setText(name_plugin)
        self.folderPlugin = (
            getAppPath() / Path(window.__class__.__module__.replace(".", os.sep)).parent
        )

        self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)

    def loader(self):
        x, y = self.win.x(), self.win.y()
        position = self._getTypeWindowTop()
        opacity = self.win.windowOpacity()
        mobility = self.win.hasMoved
        clickability = bool(
            self.win.windowFlags() & Qt.WindowType.WindowTransparentForInput
        )

        self.coordinatesWidgetX.setValue(x)
        self.coordinatesWidgetY.setValue(y)
        self.positionBox.setCurrentIndex(position)
        self.transparencySpinBox.setValue(opacity * 100)
        self.mobilityBox.setChecked(mobility)
        self.clickabilityBox.setChecked(clickability)

    def _getTypeWindowTop(self):
        if self.win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            return 2
        if self.win.windowFlags() & Qt.WindowType.WindowStaysOnBottomHint:
            return 0
        return 1

    def confirming(self):
        self.win.restoreConfig(Box(self.preSendData()))

    def preSendData(self):
        position = self.positionBox.currentIndex()

        data = {
            "position": position,
            "coordinates": QPoint(
                self.coordinatesWidgetX.value(), self.coordinatesWidgetY.value()
            ),
            "transparency": self.transparencySpinBox.value() / 100,
            "mobility": self.mobilityBox.checkState() == Qt.CheckState.Checked,
            "TranspFI": self.clickabilityBox.checkState() == Qt.CheckState.Checked,
        }
        return data

    def canceling(self):
        self.loader()

    def openFolderPlugin(self):
        open_file_manager(self.folderPlugin)
