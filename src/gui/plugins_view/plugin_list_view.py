from __future__ import annotations
import logging
from typing import Optional, List

from PySide6.QtWidgets import QListView
from PySide6.QtCore import Signal, QPoint

from plugins.items import PluginItemRole, PluginItem

from .plugin_model import PluginDataModel
from .plugin_delegate import PluginDelegate

# Initialize logger for this module
logger = logging.getLogger(__name__)


class PluginList(QListView):
    itemChecked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            logger.debug("Initializing PluginList...")
            
            self.model_data = PluginDataModel()
            self.delegate = PluginDelegate(self)
            
            self.setModel(self.model_data)
            self.setItemDelegate(self.delegate)
            
            # Connect delegate signals
            self.delegate.itemClicked.connect(self.itemChecked.emit)
            self.delegate.contextMenuRun.connect(self.contextMenuRun.emit)
            
            logger.info("PluginList initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PluginList: {e}", exc_info=True)
    
    def clear(self):
        try:
            logger.debug("Clearing all items from PluginList")
            self.model_data.clear()
        except Exception as e:
            logger.error(f"Failed to clear plugin list: {e}", exc_info=True)
    
    def addItem(self, item: PluginItem):
        try:
            if item:
                self.model_data.addItem(item)
                logger.debug(f"Added plugin item: {item}")
            else:
                logger.warning("Attempted to add None item to PluginList")
        except Exception as e:
            logger.error(f"Failed to add item to list: {e}", exc_info=True)
    
    def itemAt(self, pos: QPoint) -> Optional[PluginItem]:
        try:
            idx = self.indexAt(pos)
            if not idx.isValid():
                return None
            return self.model().data(idx, PluginItemRole.SELF)
        except Exception as e:
            logger.error(f"Failed to retrieve item at position {pos}: {e}", exc_info=True)
            return None
    
    def remove(self, item: PluginItem):
        try:
            logger.debug(f"Removing item: {item}")
            idx = self.model_data.findIndexItem(item)
            if idx.isValid():
                self.model_data.removeItem(idx)
            else:
                logger.warning(f"Could not find item to remove: {item}")
        except Exception as e:
            logger.error(f"Failed to remove item: {e}", exc_info=True)
    
    def items(self) -> List[PluginItem]:
        try:
            return self.model_data.items()
        except Exception as e:
            logger.error(f"Failed to retrieve items list: {e}", exc_info=True)
            return []
    
    def findItemBySaveName(self, saveName: str) -> Optional[PluginItem]:
        try:
            logger.debug(f"Searching for item with save_name: {saveName}")
            objs = [
                item for item in self.model_data.items()
                if isinstance(item, PluginItem) and item.save_name == saveName
            ]
            
            if objs:
                return objs[0]
            
            logger.debug(f"No item found for save_name: {saveName}")
            return None
        except Exception as e:
            logger.error(f"Error searching for item by save name '{saveName}': {e}", exc_info=True)
            return None
