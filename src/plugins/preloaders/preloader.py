import logging
import importlib
from types import ModuleType
from abc import ABC, abstractmethod, ABCMeta

from PySide6.QtWidgets import QMenu
from ldt import LDT, NexusStore
from ldt.io_drives.drivers.extra import Json5Driver

from core.common import APIBaseWidget
from utils.fs import getAppPath
from plugins.items import PluginItem

# Initialize logger for this module
logger = logging.getLogger(__name__)


class MetaSingToolsPreloader(ABCMeta):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class PreLoader(ABC, metaclass=MetaSingToolsPreloader):
    instances = {}
    configs = NexusStore(getAppPath() / "configs" / "configs_plugins.json5", Json5Driver(), preload=False)
    
    @classmethod
    def loadConfigs(cls):
        cls.configs.clear()
        try:
            logger.debug("Loading plugin configurations...")
            cls.configs.load()
        except Exception as e:
            logger.warning(f"Failed to load plugin configurations, syncing defaults: {e}")
            cls.configs.sync()
    
    @classmethod
    def load_group(cls, group_name: str, settings: NexusStore, parent):
        try:
            with settings.group_context(group_name):
                child_groups = settings.childGroups()
                logger.debug(f"Loading group '{group_name}' with {len(child_groups)} items")
                
                for item_name in child_groups:
                    try:
                        # Clean up existing items if reloading
                        old_item = parent.listPlugins.findItemBySaveName(item_name)
                        if old_item is not None:
                            logger.debug(f"Removing existing instance of '{item_name}' before reload")
                            parent.listPlugins.remove(old_item)
                        
                        target, item = cls.loaded(settings, item_name, parent)
                        yield target, item
                    
                    except ModuleNotFoundError:
                        logger.warning(f"[{group_name}] Module not found for: {item_name}")
                    except Exception as e:
                        logger.error(f"[{group_name}] Critical load error for {item_name}: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Failed to access settings group '{group_name}': {e}", exc_info=True)
    
    @classmethod
    def saveConfigs(cls):
        try:
            cls.configs.sync()
            logger.debug("Plugin configurations synced to disk")
        except Exception as e:
            logger.error(f"Failed to save configs: {e}", exc_info=True)
    
    @classmethod
    def saved(cls, target: APIBaseWidget, item: PluginItem, setting: NexusStore):
        try:
            with setting.group_context(item.save_name):
                if target is not None:
                    cls.configs.setValue(item.save_name, target.save_status())
                
                setting.setValue("module", item.module.__name__)
                setting.setValue("active", item.active)
                setting.setValue("orig_name", item.plugin_name)
                
                cls.overSaved(item, setting)
        except Exception as e:
            logger.error(f"Failed to save state for plugin '{item.save_name}': {e}", exc_info=True)
    
    @classmethod
    def loaded(cls, setting: NexusStore, name: str, parent):
        try:
            with setting.group_context(name):
                active = setting.value("active", False)
                module_name = setting.value("module")
                
                logger.debug(f"Importing module: {module_name}")
                module = importlib.import_module(module_name)
                
                origname = setting.value("orig_name", name.rsplit("_", 1)[0])
                
                parameters = [
                    module,
                    active,
                    *cls.getParameterCreateItem(setting, name, parent),
                ]
                
                item = cls.overCreateItem(*parameters)
                item.plugin_name = origname
                
                target = cls.overLoaded(setting, name, parent)
                
                if active:
                    target = item.build(parent)
                    cls.loadConfigInItem(item)
                    cls.activatedWidget(active, target)
            
            return target, item
        
        except ImportError as e:
            logger.error(f"Failed to import module for '{name}': {e}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Error loading plugin '{name}': {e}", exc_info=True)
            raise e
    
    @classmethod
    def loadConfigInItem(cls, item: PluginItem):
        try:
            if item.widget is None:
                return
            
            config_data = cls.configs.value(item.save_name, LDT())
            item.widget.load_status(config_data)
        except Exception as e:
            logger.error(f"Failed to load config into item '{item.save_name}': {e}", exc_info=True)
    
    @classmethod
    @abstractmethod
    def overCreateItem(cls, module: ModuleType, name_type: str, checked: bool = False) -> PluginItem:
        return PluginItem(module=module, active=checked, module_type=name_type)
    
    @classmethod
    @abstractmethod
    def overSaved(cls, item: PluginItem, setting: NexusStore):
        pass
    
    @classmethod
    @abstractmethod
    def overLoaded(cls, setting: NexusStore, name: str, parent) -> APIBaseWidget:
        pass
    
    @classmethod
    @abstractmethod
    def getParameterCreateItem(cls, setting: NexusStore, name: str, parent):
        return []
    
    @classmethod
    @abstractmethod
    def activatedWidget(cls, state, target):
        pass
    
    @classmethod
    @abstractmethod
    def duplicate(cls, item: PluginItem):
        return item.clone()
    
    @classmethod
    @abstractmethod
    def createActionMenu(cls, menu: QMenu, widget: APIBaseWidget, item: PluginItem):
        try:
            act_reload_c = menu.addAction("Reload Config")
            act_reload_c.triggered.connect(widget.reload_config)
            act_settings = menu.addAction("Settings")
            
            return {"settings": act_settings}
        except Exception as e:
            logger.error(f"Failed to create default action menu: {e}", exc_info=True)
            return {}
    
    def __init_subclass__(cls, **kwargs):
        try:
            if "type" not in kwargs:
                return
            type_name = kwargs.get("type")
            cls.instances[type_name] = cls
            logger.debug(f"Registered PreLoader for type: {type_name}")
        except Exception as e:
            logger.error(f"Error in PreLoader subclass initialization: {e}", exc_info=True)
    
    @classmethod
    def clear(cls, setting: NexusStore):
        try:
            for name in cls.instances.keys():
                setting.remove(f"{name}s")
            logger.debug("Cleared all plugin settings groups")
        except Exception as e:
            logger.error(f"Failed to clear settings: {e}", exc_info=True)
    
    @classmethod
    def save(cls, item: PluginItem, setting: NexusStore):
        try:
            type_key = item.module_type.lower()
            if type_key not in cls.instances:
                logger.warning(f"No PreLoader found for type: {type_key}")
                return
            
            preloader: PreLoader = cls.instances[type_key]
            
            with setting.group_context(f"{type_key}s"):
                preloader.saved(item.widget, item, setting)
        
        except Exception as e:
            logger.error(f"Failed to save plugin item '{item.plugin_name}': {e}", exc_info=True)
    
    @classmethod
    def createMenu(cls, menu: QMenu, widget, item: PluginItem):
        try:
            type_key = item.module_type.lower()
            if type_key in cls.instances:
                preloader: PreLoader = cls.instances[type_key]
                return preloader.createActionMenu(menu, widget, item)
            
            logger.warning(f"Cannot create menu, unknown type: {type_key}")
            return {}
        except Exception as e:
            logger.error(f"Failed to dispatch menu creation: {e}", exc_info=True)
            return {}
