import os
from pathlib import Path

from PySide6.QtCore import QPoint
from box import Box

from uis.dialogSettingsTemplate_ui import Ui_Form
from APIService.path_controls import getAppPath
from APIService.openFolderExplorer import open_file_manager
from API.config import Config
from API.core import APIBaseWidget

from .overlayWidget import OverlayWidget


class PluginSettingTemplate(OverlayWidget, Ui_Form):
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(Config(__file__, "overlay_widget", "settings", False), parent)
        self.setupUi(self)
        
        self.obj: APIBaseWidget = obj
        self.labelNamePlugin.setText(name_plugin)
        self.folder = getAppPath() / Path(obj.__class__.__module__.replace(".", os.sep)).parent
        
        self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)
        self.buttonBox.accepted.connect(self.confirming)
        self.buttonBox.rejected.connect(self.canceling)
    
    def openFolderPlugin(self):
        open_file_manager(self.folder)
    
    def confirming(self):
        self.obj.restoreConfig(Box(self.send_data(), default_box=True))
    
    def canceling(self):
        self.loader()
    
    def loader(self):
        self.spinBoxX.setValue(self.obj.x())
        self.spinBoxY.setValue(self.obj.y())
        super().loader()
    
    def send_data(self):
        return {
            "position": QPoint(self.spinBoxX.value(), self.spinBoxY.value())
        }
