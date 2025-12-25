from abc import ABC, ABCMeta, abstractmethod

from PySide6.QtCore import QTimer
from pydantic import BaseModel
from PySide6.QtWidgets import QWidget


class MetaBaseWidget(ABCMeta, type(QWidget)): ...


class APIBaseWidget(ABC, metaclass=MetaBaseWidget):
    dumper: "Dumper"
    config: "Config"
    _config_data_: BaseModel = None
    timer: QTimer
    time_msec: int
    
    @abstractmethod
    def reloadConfig(self): ...
    
    @abstractmethod
    def __save_config__(self) -> dict: ...
    
    @abstractmethod
    def save_config(self) -> BaseModel: ...
    
    @abstractmethod
    def __restore_config__(self, config: BaseModel): ...
    @abstractmethod
    def restore_config(self, config: dict): ...
    
    def ready(self):
        self.__ready__()
        self.timer.start(self.time_msec)
        self.__process__()
    
    @abstractmethod
    def __ready__(self): ...
    
    def process(self):
        try:
            if self.isVisible():
                self.__process__()
        except Exception as e:
            self.timer.stop()
            print(f"Error in plugin {self.config.name}: {e}")
        
    
    @abstractmethod
    def __process__(self): ...
    
    @classmethod
    def createSettingWidget(cls, obj: "APIBaseWidget", name_plugin, parent: "Overlay"): ...
