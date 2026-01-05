from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot

from plugins.items import PluginItemRole, PluginItem, PluginBadItem


class PluginDataModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._plugins: list[PluginItem | PluginBadItem] = []
    
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
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return self._plugins[index.row()].plugin_name
            case Qt.ItemDataRole.DisplayRole:
                return self._plugins[index.row()].icon
            case PluginItemRole.TYPE_ROLE:
                return self._plugins[index.row()].module_type
            case PluginItemRole.IS_DUPLICATE:
                return self._plugins[index.row()].is_duplicate
            case PluginItemRole.ACTIVE_ROLE:
                return self._plugins[index.row()].active
            case PluginItemRole.ICON:
                return self._plugins[index.row()].icon
            case PluginItemRole.SELF:
                return self._plugins[index.row()]
            case Qt.ItemDataRole.ToolTipRole:
                if self.data(index, PluginItemRole.IS_BAD):
                    return self._plugins[index.row()].getErrorStr(), "#ffe0e0"
                if self._plugins[index.row()].widget is not None:
                    return "Работает корректно", "#26fc75"
                else:
                    return "Импортировано успешно", "#26fc75"
            case PluginItemRole.IS_BAD:
                return isinstance(self._plugins[index.row()], PluginBadItem)
            case PluginItemRole.ERROR if self.data(index, PluginItemRole.IS_BAD):
                return self._plugins[index.row()].error
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.DisplayRole):
        if role == PluginItemRole.ACTIVE_ROLE:
            self.updateStateItem(value)
    
    def roleNames(self, /):
        names = super().roleNames()
        names[PluginItemRole.TYPE_ROLE] = QByteArray(b"type_plugin")
        names[PluginItemRole.ACTIVE_ROLE] = QByteArray(b"active")
        names[PluginItemRole.ICON] = QByteArray(b"icon")
        return names
    
    @Slot(int, bool)
    def updateStateItem(self, index, state):
        self._plugins[index].active = state
        idx = self.createIndex(index, 0)
        self.dataChanged.emit(idx, idx, [PluginItemRole.ACTIVE_ROLE])
    
    def items(self):
        return self._plugins[:]
