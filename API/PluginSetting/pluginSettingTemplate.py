import os
from pathlib import Path

from PySide6.QtCore import QPoint
from box import Box

from uis.dialogSettingsTemplate_ui import Ui_Form
from PathControl import getAppPath
from PathControl.openFolderExplorer import open_file_manager
from API.config import Config
from Common.core import APIBaseWidget

from .overlayWidget import OverlayWidget


class PluginSettingTemplate(OverlayWidget, Ui_Form):
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(Config("PluginSetting", "setting"), parent)
        self.setupUi(self)
        
        self.obj: APIBaseWidget = obj
        self.labelNamePlugin.setText(name_plugin)
        
        self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)
        self.buttonBox.accepted.connect(self.confirming)
        self.buttonBox.rejected.connect(self.canceling)
    
    def openFolderPlugin(self):
        open_file_manager(getAppPath()/"plugins"/f"{self.obj.config.plugin_name}.plugin")
    
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
