from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, ABCMeta, abstractmethod
import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from ldt import LDT

if TYPE_CHECKING:
    from core.config import Config
    from plugins.preloaders import PreLoader
    from gui.main_window import Overlay

logger = logging.getLogger(__name__)


class MetaBaseWidget(ABCMeta, type(QWidget)):
    ...


class APIBaseWidget(QWidget, ABC, metaclass=MetaBaseWidget):
    dumper: PreLoader
    config: Config
    timer: QTimer
    time_msec: int
    
    @abstractmethod
    def reload_config(self):
        ...
    
    @abstractmethod
    def save_status(self) -> LDT:
        ...
    
    @abstractmethod
    def load_status(self, status: LDT):
        ...
    
    @abstractmethod
    def load_config(self):
        ...
    
    def ready(self):
        try:
            self.__ready__()
            self.timer.start(self.time_msec)
            self.__process__()
            
            name = getattr(self.config, "name", "Unknown Widget")
            logger.info(f"Widget '{name}' started successfully.")
        
        except Exception as e:
            logger.warning(f"Error not read widget: {e}")
            logger.error("Failed to start widget:", exc_info=True)
    
    @abstractmethod
    def __ready__(self):
        ...
    
    def process(self):
        try:
            if self.isVisible():
                self.__process__()
        except Exception as e:
            self.timer.stop()
            name = "Unknown"
            if hasattr(self, 'config') and hasattr(self.config, 'name'):
                name = self.config.name
            logger.warning(f"Plugin '{name}' stopped. Error: {e}")
            logger.error(f"Crash in plugin '{name}'", exc_info=True)
    
    @abstractmethod
    def __process__(self):
        ...
    
    @classmethod
    def createSettingWidget(cls, obj: APIBaseWidget, name_plugin, parent: Overlay):
        ...
