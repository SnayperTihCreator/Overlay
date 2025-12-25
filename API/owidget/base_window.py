import uuid
from abc import ABC
from enum import IntEnum, auto

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from pydantic import BaseModel

from API.config import Config
from Common.core import APIBaseWidget

from ApiPlugins.widgetPreloader import WidgetPreLoader
from .pluginSettingWidget import PluginSettingWidget, WidgetConfigData
from ColorControl.themeController import ThemeController


class ModeRuns(IntEnum):
    AUTO = auto()
    VISIBLE_OVERLAY = auto()
    VISIBLE_WIDGET = auto()


class OWidget(QWidget, APIBaseWidget, ABC):
    dumper = WidgetPreLoader()
    _config_data_ = WidgetConfigData
    
    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowType.Widget)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        self.uid = uuid.uuid4().hex
        
        self.running = False
        self.mode: ModeRuns = ModeRuns.AUTO
        
        self.config: Config = config
        self.time_msec = 1000
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        
        QTimer.singleShot(0, self.loadConfig)
    
    def __ready__(self):
        ...
    
    def process(self):
        match self.mode:
            case ModeRuns.AUTO | ModeRuns.VISIBLE_WIDGET if self.running:
                self.__process__()
            case ModeRuns.VISIBLE_OVERLAY:
                super().process()
    
    def setActive(self, state):
        self.running = state
    
    def __process__(self):
        ...
    
    def reloadConfig(self):
        self.config.reload()
        self.loadConfig()
    
    def save_config(self) -> BaseModel:
        return self._config_data_(**self.__save_config__())
    
    def __save_config__(self) -> dict:
        return {"position": self.pos()}
    
    def restore_config(self, config: dict):
        self.__restore_config__(self._config_data_(**config))
    
    def __restore_config__(self, config: BaseModel):
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
    def createSettingWidget(cls, widget: "owidget", name_plugin: str, parent):
        return PluginSettingWidget(widget, name_plugin, parent)
