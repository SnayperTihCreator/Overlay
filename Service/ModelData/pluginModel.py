from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot

from ApiPlugins.pluginItems import PluginItem, PluginItemRole


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
    
    def findIndexItem(self, item):
        idx = self._plugins.index(item)
        return self.createIndex(idx, 0)
    
    def clear(self):
        self.beginResetModel()
        self._plugins.clear()
        self.endResetModel()
    
    def rowCount(self, /, parent=None):
        return len(self._plugins)
    
    def data(self, index, /, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._plugins[index.row()].namePlugin
        if role == Qt.ItemDataRole.DecorationRole:
            return self._plugins[index.row()].icon
        if role == PluginItemRole.TypePluginRole:
            return self._plugins[index.row()].typeModule
        if role == PluginItemRole.Duplication:
            return self._plugins[index.row()].isDuplication
        if role == PluginItemRole.ActiveRole:
            return self._plugins[index.row()].active
        if role == PluginItemRole.Icon:
            return self._plugins[index.row()].icon
        if role == PluginItemRole.Self:
            return self._plugins[index.row()]
    
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
    
    def items(self):
        return self._plugins[:]