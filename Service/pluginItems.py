from enum import IntEnum, auto
from functools import cached_property
from types import ModuleType

from PySide6.QtCore import Qt, qWarning
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget
from attrs import define, field

from API.core import APIBaseWidget

__all__ = ["PluginItemRole", "PluginItem"]


class PluginItemRole(IntEnum):
    TypePluginRole = Qt.ItemDataRole.UserRole
    ActiveRole = auto()
    Self = auto()
    Icon = auto()
    Duplication = auto()


@define
class PluginItem:
    module: ModuleType = field()
    typeModule: str = field()
    active: bool = field(default=False)
    
    namePlugin: str = field(default=None, init=False)
    countClone: int = field(default=0, init=False, repr=False)
    isDuplication: bool = field(default=False, init=False, repr=False)
    widget: APIBaseWidget | QWidget = field(init=False, default=None, repr=False)
    
    def __attrs_post_init__(self):
        self.namePlugin = self.module.__name__
    
    @cached_property
    def save_name(self):
        return f"{self.namePlugin}_{self.typeModule}"
    
    @property
    def icon(self):
        return QPixmap()
    
    def clone(self):
        item = PluginItem(self.module, self.typeModule)
        item.isDuplication = True
        item.namePlugin = f"{self.namePlugin}_{self.countClone+1:04d}"
        self.countClone += 1
        return item
    
    def updateStateItem(self, state):
        self.active = state
    
    @property
    def iconData(self):
        try:
            return open(f"plugin://{self.module.__name__}/icon.png", "rb").read()
        except Exception as e:
            qWarning(f"{type(e)}: {e}")
            return None
        
    def build(self, parent):
        if self.widget is None:
            match self.typeModule:
                case "Window":
                    self.widget = self.module.createWindow(parent)
                case "Widget":
                    self.widget = self.module.createWidget(parent)
        return self.widget
