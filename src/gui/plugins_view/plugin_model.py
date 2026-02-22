from __future__ import annotations
import logging
from typing import Any, Union, List

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot

from plugins.items import PluginItemRole, PluginItem, PluginBadItem, PluginBase

# Initialize logger for this module
logger = logging.getLogger(__name__)


class PluginDataModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._plugins: List[Union[PluginItem, PluginBadItem]] = []
        logger.debug("PluginDataModel initialized")
    
    def addItem(self, item: PluginBase):
        try:
            if not isinstance(item, PluginBase):
                logger.error(f"Attempted to add invalid item type: {type(item)}")
                raise TypeError("Item must be an instance of PluginBase")
            
            # Use strict layout change signaling
            self.beginInsertRows(QModelIndex(), len(self._plugins), len(self._plugins))
            self._plugins.append(item)
            self.endInsertRows()
            
            logger.debug(f"Added plugin item: {getattr(item, 'plugin_name', 'Unknown')}")
        
        except Exception as e:
            logger.error(f"Failed to add item to model: {e}", exc_info=True)
    
    def removeItem(self, index: QModelIndex) -> bool:
        try:
            row = index.row()
            if 0 <= row < len(self._plugins):
                self.beginRemoveRows(QModelIndex(), row, row)
                removed_item = self._plugins.pop(row)
                self.endRemoveRows()
                
                logger.debug(f"Removed plugin item: {getattr(removed_item, 'plugin_name', 'Unknown')}")
                return True
            
            logger.warning(f"Attempted to remove item at invalid index: {row}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to remove item: {e}", exc_info=True)
            return False
    
    def findIndexItem(self, item) -> QModelIndex:
        try:
            if item in self._plugins:
                idx = self._plugins.index(item)
                return self.createIndex(idx, 0)
            
            logger.debug("Item not found in model during search")
            return QModelIndex()
        
        except Exception as e:
            logger.error(f"Error finding item index: {e}", exc_info=True)
            return QModelIndex()
    
    def clear(self):
        try:
            logger.debug("Clearing PluginDataModel")
            self.beginResetModel()
            self._plugins.clear()
            self.endResetModel()
        except Exception as e:
            logger.error(f"Failed to clear model: {e}", exc_info=True)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._plugins)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole) -> Any:
        try:
            if not index.isValid():
                return None
            
            row = index.row()
            if row < 0 or row >= len(self._plugins):
                return None
            
            item = self._plugins[row]
            
            # Match Roles
            if role == Qt.ItemDataRole.DisplayRole:
                return item.plugin_name
            
            elif role == Qt.ItemDataRole.DecorationRole:
                # Fixed: Changed duplicate DisplayRole to DecorationRole for icon
                return item.icon
            
            elif role == PluginItemRole.TYPE_ROLE:
                return item.module_type
            
            elif role == PluginItemRole.IS_DUPLICATE:
                return getattr(item, 'is_duplicate', False)
            
            elif role == PluginItemRole.ACTIVE_ROLE:
                return getattr(item, 'active', False)
            
            elif role == PluginItemRole.ICON:
                return item.icon
            
            elif role == PluginItemRole.SELF:
                return item
            
            elif role == Qt.ItemDataRole.ToolTipRole:
                # Check if it is a "Bad" item first
                is_bad = isinstance(item, PluginBadItem)
                
                if is_bad:
                    # Return tuple (Text, Color)
                    return item.getErrorStr(), "#ffe0e0"
                
                if getattr(item, 'widget', None) is not None:
                    return "Working correctly", "#26fc75"
                else:
                    return "Imported successfully", "#26fc75"
            
            elif role == PluginItemRole.IS_BAD:
                return isinstance(item, PluginBadItem)
            
            elif role == PluginItemRole.ERROR:
                # Only return error if it is bad
                if isinstance(item, PluginBadItem):
                    return item.error
            
            return None
        
        except Exception as e:
            # We log minimal info here to avoid flooding logs during render loops
            logger.error(f"Error retrieving data for row {index.row()}, role {role}: {e}", exc_info=True)
            return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.DisplayRole) -> bool:
        try:
            if not index.isValid():
                return False
            
            if role == PluginItemRole.ACTIVE_ROLE:
                self.updateStateItem(index.row(), value)
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to set data: {e}", exc_info=True)
            return False
    
    def roleNames(self):
        try:
            names = super().roleNames()
            names[PluginItemRole.TYPE_ROLE] = QByteArray(b"type_plugin")
            names[PluginItemRole.ACTIVE_ROLE] = QByteArray(b"active")
            names[PluginItemRole.ICON] = QByteArray(b"icon")
            return names
        except Exception as e:
            logger.error(f"Failed to get role names: {e}", exc_info=True)
            return {}
    
    @Slot(int, bool)
    def updateStateItem(self, index: int, state: bool):
        try:
            if 0 <= index < len(self._plugins):
                item = self._plugins[index]
                if hasattr(item, 'active'):
                    item.active = state
                    
                    idx = self.createIndex(index, 0)
                    self.dataChanged.emit(idx, idx, [PluginItemRole.ACTIVE_ROLE])
                    
                    logger.info(f"Updated state for '{item.plugin_name}': {'Active' if state else 'Inactive'}")
                else:
                    logger.warning(f"Item at index {index} has no 'active' attribute")
            else:
                logger.warning(f"Index out of bounds in updateStateItem: {index}")
        
        except Exception as e:
            logger.error(f"Failed to update item state: {e}", exc_info=True)
    
    def items(self) -> List[Union[PluginItem, PluginBadItem]]:
        return self._plugins[:]
