import uuid
import logging
from abc import ABC
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, QTimer

from core.common import APIBaseWidget
from core.config import Config
from plugins.flags_installer import FlagsInstaller
from plugins.preloaders import WidgetPreLoader
from gui.themes import ThemeController
from ldt import LDT

from .settings import PluginSettingWidget

if TYPE_CHECKING:
    from gui.main_window import Overlay

# Setup logger
logger = logging.getLogger(__name__)


class ModeRuns(IntEnum):
    AUTO = auto()
    VISIBLE_OVERLAY = auto()
    VISIBLE_WIDGET = auto()


class OWidget(APIBaseWidget, ABC):
    dumper = WidgetPreLoader()
    
    def __init__(self, config, parent=None):
        # We don't call super().__init__ here? Usually QWidget needs it.
        # Assuming APIBaseWidget calls QWidget.__init__ or similar.
        # If APIBaseWidget inherits QWidget directly, super().__init__(parent) is correct.
        super().__init__(parent, Qt.WindowType.Widget)
        
        self.flagsInstaller: FlagsInstaller = FlagsInstaller.bind(self)
        self.flagsInstaller.install(Qt.WindowType.Widget)
        
        self.overlay: Optional[Overlay] = parent
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        self.uid = uuid.uuid4().hex
        
        self.running = False
        self.mode: ModeRuns = ModeRuns.AUTO
        
        self.config: Config = config
        self.time_msec = 1000
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        
        logger.info(f"OWidget initialized: {self.config.name} (UID: {self.uid})")
        
        QTimer.singleShot(0, self.load_config)
    
    def __ready__(self):
        # Optional hook for subclasses
        pass
    
    def process(self):
        try:
            match self.mode:
                case ModeRuns.AUTO | ModeRuns.VISIBLE_WIDGET if self.running:
                    self.__process__()
                case ModeRuns.VISIBLE_OVERLAY:
                    super().process()  # This calls APIBaseWidget.process which has logging
        except Exception as e:
            # If crash happens here (outside APIBaseWidget.process scope for some reason)
            logger.error(f"Error in OWidget process ({self.config.name}): {e}", exc_info=True)
            self.timer.stop()
    
    def setActive(self, state):
        if self.running != state:
            self.running = state
            logger.debug(f"Widget '{self.config.name}' active state changed to: {state}")
    
    def __process__(self):
        ...
    
    def reload_config(self):
        logger.info(f"Reloading config for widget: {self.config.name}")
        try:
            self.config.reload()
            self.load_config()
        except Exception as e:
            logger.error(f"Failed to reload config for {self.config.name}: {e}", exc_info=True)
    
    def save_status(self) -> LDT:
        ldt = LDT()
        ldt.set("position", self.pos())
        return ldt
    
    def load_status(self, status: LDT):
        ...
    
    def load_config(self):
        try:
            style_file = self.config.data.settings.style_file
            theme_path = f"plugin://{self.config.name}/{style_file}"
            
            ThemeController().register(self, theme_path, False)
            ThemeController().updateUid(self.uid)
            
            logger.debug(f"Config loaded for widget: {self.config.name}")
        except Exception as e:
            logger.error(f"Error loading widget config/theme ({self.config.name}): {e}", exc_info=True)
    
    def gridOverlay(self, anchorX, anchorY):
        if self.overlay:
            self.overlay.addWidget(self, [anchorX, anchorY])
        else:
            logger.warning(f"Cannot grid widget '{self.config.name}': No overlay parent.")
    
    @classmethod
    def createSettingWidget(cls, widget: "OWidget", name_plugin: str, parent):
        return PluginSettingWidget(widget, name_plugin, parent)