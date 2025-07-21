from types import ModuleType
from enum import IntEnum, auto
from typing import Any, Union
from functools import cache

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, QUrl, Slot
from PySide6.QtWidgets import QWidget
from attrs import define, field

from API.core import APIBaseWidget


class PluginItemRole(IntEnum):
    TypePluginRole = Qt.ItemDataRole.UserRole
    ActiveRole = auto()
    IconPath = auto()
    Icon = auto()
    Duplication = auto()


@define
class PluginItem:
    namePlugin: str = field(default=None, init=False)
    module: ModuleType = field()
    iconPath: str = field()
    typeModule: str = field()
    parent: Any = field()
    active: bool = field(default=False)
    
    _widget: Union[APIBaseWidget, QWidget] = field(init=False, default=None)
    
    def updateStateItem(self, state):
        self.initialisation()
        self._widget.dumper.activatedWidget(state, self._widget)
        self.active = state
            
    def initialisation(self):
        if self._widget is None:
            self.buildItem()
            
    def __attrs_post_init__(self):
        self.namePlugin = self.module.__name__
    
    def buildItem(self):
        match self.typeModule:
            case "Window":
                self._widget = self.module.createWindow(self.parent)
            case "Widget":
                self._widget = self.module.createWidget(self.parent)
    
    @property
    @cache
    def save_name(self):
        return f"{self.namePlugin}_{self.typeModule}"
    
    @property
    def icon(self):
        self.initialisation()
        return self._widget.dumper.getIcon(self.namePlugin)
            

@define
class ClonePluginItem(PluginItem):
    countClone: int = field(default=0, init=False, repr=False)
    isDuplication: bool = field(default=False, init=False, repr=False)
    
    def clone(self):
        item = ClonePluginItem(self.module, self.iconPath, self.typeModule, self.parent)
        item.isDuplication = True
        item.namePlugin = f"{self.namePlugin}_{self.countClone:03d}"
        self.countClone += 1
        return item


class PluginDataModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._plugins: list[PluginItem] = []
    
    def addItem(self, item: PluginItem):
        if not isinstance(item, PluginItem): raise TypeError
        self.beginInsertRows(QModelIndex(), len(self._plugins), len(self._plugins))
        self._plugins.append(item)
        self.endInsertRows()
    
    def removeItem(self, index):
        if 0 <= index.row() < len(self._plugins):
            self.beginRemoveRows(QModelIndex(), index.row(), index.row())
            del self._plugins[index.row()]
            self.endRemoveRows()
            return True
        return False
    
    def clear(self):
        self.beginResetModel()
        self._plugins.clear()
        self.endResetModel()
    
    def rowCount(self, /, parent=None):
        return len(self._plugins)
    
    def data(self, index, /, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._plugins[index.row()].namePlugin
        if role == PluginItemRole.IconPath:
            return self._plugins[index.row()].iconPath
        if role == PluginItemRole.TypePluginRole:
            return self._plugins[index.row()].typeModule
        if role == PluginItemRole.Duplication:
            item = self._plugins[index.row()]
            return hasattr(item, "isDuplication")
        if role == PluginItemRole.ActiveRole:
            return self._plugins[index.row()].active
        if role == PluginItemRole.Icon:
            return self._plugins[index.row()].icon
        
    def setData(self, index, value, role=Qt.ItemDataRole.DisplayRole):
        if role == PluginItemRole.ActiveRole:
            self._plugins[index.row()].updateStateItem(value)
    
    def roleNames(self, /):
        names = super().roleNames()
        names[PluginItemRole.TypePluginRole] = QByteArray(b"type_plugin")
        names[PluginItemRole.ActiveRole] = QByteArray(b"active")
        names[PluginItemRole.IconPath] = QByteArray(b"iconPath")
        return names
    
    @Slot(int, bool)
    def updateStateItem(self, index, state):
        self._plugins[index].updateStateItem(state)
        idx = self.createIndex(index, 0)
        self.dataChanged.emit(idx, idx, [PluginItemRole.ActiveRole])
        
    
