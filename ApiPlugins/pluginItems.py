from enum import IntEnum, auto
from functools import cached_property
from types import ModuleType, NoneType
from traceback import format_exception

from PySide6.QtCore import Qt, qWarning
from PySide6.QtWidgets import QWidget
from attrs import define, field

from Common.core import APIBaseWidget
from ColorControl.themeController import ThemeController
from Service.errors import PluginBuild

__all__ = ["PluginItemRole", "PluginItem"]


class PluginItemRole(IntEnum):
    TypePluginRole = Qt.ItemDataRole.UserRole
    ActiveRole = auto()
    Self = auto()
    Icon = auto()
    Duplication = auto()
    BadItem = auto()
    Error = auto()


@define
class PluginItem:
    bad_item = False
    
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
        return ThemeController().getImage(f"plugin://{self.module.__name__}/icon.png")
    
    def clone(self):
        item = PluginItem(self.module, self.typeModule)
        item.isDuplication = True
        item.namePlugin = f"{self.namePlugin}_{self.countClone+1:04d}"
        self.countClone += 1
        return item
    
    def updateStateItem(self, state):
        self.active = state
        
    def build(self, parent):
        if self.widget is None:
            match self.typeModule:
                case "Window":
                    self.widget = self.module.createWindow(parent)
                case "Widget":
                    self.widget = self.module.createWidget(parent)
        return self.widget


@define
class PluginBadItem(PluginItem):
    bad_item = True
    
    namePlugin: str = field(default=None)
    error: Exception = field(default=None)
    
    module: NoneType = field(init=False, default=None)
    typeModule: NoneType = field(init=False, default=None)
    active: NoneType = field(init=False, default=None)
    
    def __attrs_post_init__(self):
        pass
    
    def build(self, parent):
        raise PluginBuild(self.namePlugin)
        
    def showInfo(self):
        dataInfo = "".join(format_exception(self.error))
        qWarning(f"Ошибка импорта пакета {self.namePlugin}:\n {dataInfo}")
        
    def getErrorStr(self):
        return f"Error {type(self.error).__name__}: {self.error}"
        
    