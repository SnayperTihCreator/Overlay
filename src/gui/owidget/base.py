import uuid
from abc import ABC
from enum import IntEnum, auto

from PySide6.QtCore import Qt, QTimer

from core.common import APIBaseWidget
from core.config import Config
from plugins.preloaders import WidgetPreLoader
from gui.themes import ThemeController
from ldt import LDT

from .settings import PluginSettingWidget


class ModeRuns(IntEnum):
    AUTO = auto()
    VISIBLE_OVERLAY = auto()
    VISIBLE_WIDGET = auto()


class OWidget(APIBaseWidget, ABC):
    dumper = WidgetPreLoader()
    
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
        
        QTimer.singleShot(0, self.load_config)
    
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
    
    def reload_config(self):
        self.config.reload()
        self.load_config()
        
    def save_status(self) -> LDT:
        ldt = LDT()
        ldt.set("position", self.pos())
        return ldt
    
    def load_status(self, status: LDT):
        ...
    
    def load_config(self):
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
