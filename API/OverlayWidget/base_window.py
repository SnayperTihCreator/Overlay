from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, qWarning
from qt_material import apply_stylesheet

from API.config import Config
from API.core import APIBaseWidget

from .dumper import OverlayWidgetDumper
from API.PluginSetting import PluginSettingWidget


class OverlayWidget(QWidget, APIBaseWidget):
    dumper = OverlayWidgetDumper()
    
    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowType.Widget)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        
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
        if self.config.widget:
            try:
                apply_stylesheet(
                    self,
                    theme="dark_purple.xml",
                    extra={
                        "font_size": "14px",
                        "primaryColor": "#8b13a0",
                        "primaryTextColor": "#41fd9f",
                        "secondaryTextColor": "#9ad789",
                    },
                    css_file=self.config.plugin_path() / self.config.widget.styleFile,
                )
            except Exception as e:
                qWarning(str(e))
    
    @classmethod
    def createSettingWidget(cls, widget: "OverlayWidget", name_plugin: str, parent):
        return PluginSettingWidget(widget, name_plugin, parent)
