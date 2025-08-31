import uuid

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from pydantic import BaseModel

from API.config import Config
from Common.core import APIBaseWidget

from ApiPlugins.widgetPreloader import WidgetPreLoader
from .pluginSettingWidget import PluginSettingWidget, WidgetConfigData
from ColorControl.themeController import ThemeController


class OWidget(QWidget, APIBaseWidget):
    dumper = WidgetPreLoader()
    _config_data_ = WidgetConfigData
    
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
        
    def save_config(self) -> BaseModel:
        return self._config_data_(**self.__save_config__())
    
    def __save_config__(self) -> dict:
        return {"position": self.pos()}
    
    def restore_config(self, config: dict):
        self.__restore_config__(self._config_data_(**config))
        
    def __restore_config__(self, config: BaseModel):
        pass
    
    def loader(self):
        pass
    
    def loadConfig(self):
        ThemeController().register(self,
                                   f"plugin://{self.config.name}/{self.config.data.widget.styleFile}",
                                   False)
        ThemeController().updateUid(self.uid)
        
    def gridOverlay(self, anchorX, anchorY):
        self.parent().addWidget(
            self,
            [anchorX, anchorY]
        )
    
    @classmethod
    def createSettingWidget(cls, widget: "OWidget", name_plugin: str, parent):
        return PluginSettingWidget(widget, name_plugin, parent)
