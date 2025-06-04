import os

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from API.config import Config

from .dumper import OverlayWidgetDumper


class OverlayWidget(QWidget):
    dumper = OverlayWidgetDumper()
    
    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowType.Widget)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        
        self.config: Config = config
    
    def reloadConfig(self):
        self.config.reload()
        self.loader()
    
    def savesConfig(self):
        return {}
    
    def restoreConfig(self, config):
        pass
    
    def loader(self):
        pass
    
    @classmethod
    def createSettingWidget(cls, widget: "OverlayWidget", name_plugin: str, parent):
        # return PluginSettingsWidget(window, name_plugin, parent)
        return
