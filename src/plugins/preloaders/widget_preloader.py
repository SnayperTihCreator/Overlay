import logging
from types import ModuleType
from typing import Optional, List

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu

from .preloader import PreLoader
from plugins.items import PluginItem

# Initialize logger for this module
logger = logging.getLogger(__name__)


class WidgetPreLoader(PreLoader, type="widget"):
    
    @classmethod
    def overCreateItem(cls, module: ModuleType, checked: bool = False, **kwargs) -> Optional[PluginItem]:
        try:
            logger.debug(f"Creating widget item for module: {module.__name__}")
            return super().overCreateItem(module, "Widget", checked)
        except Exception as e:
            logger.error(f"Failed to create widget item: {e}", exc_info=True)
            return None
    
    @classmethod
    def overSaved(cls, item: PluginItem, setting: QSettings):
        # No specific saving logic for basic widgets
        return None
    
    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent):
        # Widgets usually don't need complex reloading logic here, 
        # as they are rebuilt via build() method later
        return None
    
    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent) -> List:
        return []
    
    @classmethod
    def activatedWidget(cls, state: bool, target):
        try:
            if target is None:
                logger.warning("Attempted to activate None widget target")
                return
            
            logger.debug(f"Setting widget active state to: {state}")
            target.setActive(state)
            
            if state:
                target.ready()
                target.show()
                logger.info(f"Widget activated and shown: {target.objectName()}")
            else:
                target.hide()
                logger.info(f"Widget deactivated and hidden: {target.objectName()}")
        
        except Exception as e:
            logger.error(f"Failed to change widget activation state: {e}", exc_info=True)
    
    @classmethod
    def duplicate(cls, item: PluginItem):
        logger.warning("Duplication is not implemented for Widgets")
        return NotImplemented
    
    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: PluginItem):
        try:
            return super().createActionMenu(menu, widget, item)
        except Exception as e:
            logger.error(f"Failed to create action menu for widget: {e}", exc_info=True)
            return {}
