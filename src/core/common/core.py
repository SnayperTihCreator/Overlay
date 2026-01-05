from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, ABCMeta, abstractmethod

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from utils.ldt import LDT

if TYPE_CHECKING:
    from core.config import Config
    from plugins.preloaders import PreLoader
    from gui.main_window import Overlay


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
    def save_status(self) -> LDT: ...
    
    @abstractmethod
    def load_status(self, status: LDT): ...
    
    @abstractmethod
    def load_config(self): ...
    
    def ready(self):
        self.__ready__()
        self.timer.start(self.time_msec)
        self.__process__()
    
    @abstractmethod
    def __ready__(self):
        ...
    
    def process(self):
        try:
            if self.isVisible():
                self.__process__()
        except Exception as e:
            self.timer.stop()
            print(f"Error in plugin {self.config.name}: {e}")
    
    @abstractmethod
    def __process__(self):
        ...
    
    @classmethod
    def createSettingWidget(cls, obj: APIBaseWidget, name_plugin, parent: Overlay):
        ...
