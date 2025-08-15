from abc import ABC, ABCMeta, abstractmethod

from box import Box
from PySide6.QtWidgets import QWidget


class MetaBaseWidget(ABCMeta, type(QWidget)): ...


class APIBaseWidget(ABC, metaclass=MetaBaseWidget):
    dumper: "Dumper"
    config: "Config"
    
    @abstractmethod
    def reloadConfig(self): ...
    
    @abstractmethod
    def savesConfig(self): return ...
    
    @abstractmethod
    def restoreConfig(self, config: Box): ...
    
    @classmethod
    def createSettingWidget(cls, obj: "APIBaseWidget", name_plugin, parent: "Overlay"): ...
