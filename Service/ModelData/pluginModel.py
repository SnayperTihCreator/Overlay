from types import ModuleType
from enum import IntEnum, auto

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, QUrl
from attrs import define, field


class PluginItemRole(IntEnum):
    TypePluginRole = Qt.ItemDataRole.UserRole
    ActiveRole = auto()
    IconPath = auto()


@define
class PluginItem:
    module: ModuleType = field()
    iconPath: str = field()
    type_module: str = field()
    active: bool = field(default=False)


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
            return self._plugins[index.row()].module.__name__
        if role == PluginItemRole.IconPath:
            return self._plugins[index.row()].iconPath
        if role == PluginItemRole.TypePluginRole:
            return self._plugins[index.row()].type_module
    
    def roleNames(self, /):
        names = super().roleNames()
        names[PluginItemRole.TypePluginRole] = QByteArray(b"type_plugin")
        names[PluginItemRole.ActiveRole] = QByteArray(b"active")
        names[PluginItemRole.IconPath] = QByteArray(b"iconPath")
        return names
