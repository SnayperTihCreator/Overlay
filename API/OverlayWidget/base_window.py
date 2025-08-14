import uuid

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from API.config import Config
from Common.core import APIBaseWidget

from ApiPlugins.widgetPreloader import WidgetPreLoader
from API.PluginSetting import PluginSettingWidget
from ColorControl.themeController import ThemeController


class OverlayWidget(QWidget, APIBaseWidget):
    dumper = WidgetPreLoader()
    
    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowType.Widget)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        self.uid = uuid.uuid4().hex
        
        self.config: Config = config
        
        self.loadConfig()
    
    def reloadConfig(self):
        self.config.reload()
        self.loader()
        
        self.loadConfig()
    
    def savesConfig(self):
        return {}
    
    def restoreConfig(self, config):
        pass
    
    def loader(self):
        pass
    
    def loadConfig(self):
        ThemeController().register(self, f"plugin://{self.config.plugin_name}/{self.config.widget.styleFile}", False)
        ThemeController().updateUid(self.uid)
    
    @classmethod
    def createSettingWidget(cls, widget: "OverlayWidget", name_plugin: str, parent):
        return PluginSettingWidget(widget, name_plugin, parent)
