import os
from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from box import Box

from uis.dialogSettingsTemplate_ui import Ui_Form
from utils import getAppPath, open_file_manager
from API.OverlayWidget import OverlayWidget
from API.config import Config


class PluginSettingTemplate(OverlayWidget, Ui_Form):
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(Config(__file__, "overlay_widget", "settings", False), parent)
        self.setupUi(self)
        
        self.obj = obj
        self.labelNamePlugin.setText(name_plugin)
        self.folder = getAppPath() / Path(obj.__class__.__module__.replace(".", os.sep)).parent
        
        self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)
        self.buttonBox.accepted.connect(self.confirming)
        self.buttonBox.rejected.connect(self.canceling)
    
    def openFolderPlugin(self):
        open_file_manager(self.folder)
    
    def confirming(self):
        pass
    
    def canceling(self):
        pass
    
    def loader(self):
        super().loader()
