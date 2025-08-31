from abc import ABC, ABCMeta, abstractmethod

from pydantic import BaseModel
from PySide6.QtWidgets import QWidget


class MetaBaseWidget(ABCMeta, type(QWidget)): ...


class APIBaseWidget(ABC, metaclass=MetaBaseWidget):
    dumper: "Dumper"
    config: "Config"
    _config_data_: BaseModel = None
    
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
    
    @classmethod
    def createSettingWidget(cls, obj: "APIBaseWidget", name_plugin, parent: "Overlay"): ...
