import logging
from typing import Optional, Any, Dict, List
from types import ModuleType

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu

from .preloader import PreLoader
from plugins.items import PluginItem
from core.common import APIBaseWidget

# Initialize logger for this module
logger = logging.getLogger(__name__)


class WindowPreLoader(PreLoader, type="window"):
    
    @classmethod
    def overCreateItem(
            cls,
            module: ModuleType,
            checked: bool = False,
            count_dup: int = 0,
            is_dup: bool = False,
    ) -> Optional[PluginItem]:
        try:
            logger.debug(f"Creating Window item from module: {module.__name__}, duplicate: {is_dup}")
            item: PluginItem = super().overCreateItem(module, "Window", checked)
            if item:
                item.clone_count = count_dup
                item.is_duplicate = is_dup
            return item
        except Exception as e:
            logger.error(f"Failed to create window item: {e}", exc_info=True)
            return None
    
    @classmethod
    def overSaved(cls, item: PluginItem, setting: QSettings):
        try:
            setting.setValue("clone_count", item.clone_count)
            setting.setValue("is_duplicate", item.is_duplicate)
            logger.debug(f"Saved window state for '{item.save_name}': clone_count={item.clone_count}")
        except Exception as e:
            logger.error(f"Failed to save window state: {e}", exc_info=True)
    
    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent) -> Optional[Any]:
        return None
    
    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent) -> List[Any]:
        try:
            clone_count = setting.value("clone_count", 0, int)
            is_duplicate = setting.value("is_duplicate", False, bool)
            return [clone_count, is_duplicate]
        except Exception as e:
            logger.error(f"Failed to retrieve create parameters: {e}", exc_info=True)
            return [0, False]
    
    @classmethod
    def activatedWidget(cls, state: bool, target: APIBaseWidget):
        try:
            if target is None:
                logger.warning("Attempted to activate None target window")
                return
            
            if state:
                logger.info(f"Activating window: {target.objectName()}")
                target.ready()
                target.show()
            else:
                logger.info(f"Deactivating window: {target.objectName()}")
                target.hide()
        except Exception as e:
            logger.error(f"Failed to toggle window activation state: {e}", exc_info=True)
    
    @classmethod
    def duplicate(cls, item: PluginItem) -> Optional[PluginItem]:
        try:
            logger.info(f"Duplicating window plugin: {item.save_name}")
            return item.clone()
        except Exception as e:
            logger.error(f"Failed to duplicate item: {e}", exc_info=True)
            return None
    
    @classmethod
    def createActionMenu(cls, menu: QMenu, widget: APIBaseWidget, item: PluginItem) -> Dict[str, Any]:
        try:
            actions = super().createActionMenu(menu, widget, item)
            
            # Highlight Border Action
            act_highlight_b = menu.addAction("Highlight Border")
            if hasattr(widget, 'highlightBorder'):
                act_highlight_b.triggered.connect(widget.highlightBorder)
            else:
                act_highlight_b.setEnabled(False)
            
            # Duplicate Action
            act_duplicate = menu.addAction("Duplicate")
            actions["duplicate"] = act_duplicate
            
            # Delete Duplicate Action (only if it is a clone)
            if getattr(item, 'is_duplicate', False):
                act_delete_d = menu.addAction("Delete Duplicate")
                actions["delete_duplicate"] = act_delete_d
            
            return actions
        
        except Exception as e:
            logger.error(f"Failed to create context menu for window: {e}", exc_info=True)
            return {}
