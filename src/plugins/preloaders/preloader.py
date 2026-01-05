import importlib
from types import ModuleType
from abc import ABC, abstractmethod, ABCMeta

from PySide6.QtCore import qWarning
from PySide6.QtWidgets import QMenu
import json5

from core.common import APIBaseWidget
from core.settings import LDTSettings, Json5Driver
from utils.ldt import LDT
from utils.fs import getAppPath
from plugins.items import PluginItem


class MetaSingToolsPreloader(ABCMeta):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class PreLoader(ABC, metaclass=MetaSingToolsPreloader):
    instances = {}
    configs = LDTSettings(getAppPath()/"configs"/"configs_plugins.json5", Json5Driver(), preload=False)
    
    @classmethod
    def loadConfigs(cls):
        cls.configs.clear()
        try:
            cls.configs.load()
        except Exception:
            cls.configs.sync()
    
    @classmethod
    def load_group(cls, group_name: str, settings: LDTSettings, parent):
        with settings.group_context(group_name):
            child_groups = settings.childGroups()
            for item_name in child_groups:
                try:
                    old_item = parent.listPlugins.findItemBySaveName(item_name)
                    if old_item is not None:
                        parent.listPlugins.remove(old_item)
                    target, item = cls.loaded(settings, item_name, parent)
                    yield target, item
                
                except ModuleNotFoundError:
                    qWarning(f"[{group_name}] Модуль не найден для: {item_name}")
                except Exception as e:
                    qWarning(f"[{group_name}] Критическая ошибка загрузки {item_name}: {e}")
    
    @classmethod
    def saveConfigs(cls):
        cls.configs.sync()
    
    @classmethod
    def saved(cls, target: APIBaseWidget, item: PluginItem, setting: LDTSettings):
        with setting.group_context(item.save_name):
            if target is not None:
                cls.configs.setValue(item.save_name, target.save_status())
            setting.setValue("module", item.module.__name__)
            setting.setValue("active", item.active)
            setting.setValue("orig_name", item.plugin_name)
            cls.overSaved(item, setting)
    
    @classmethod
    def loaded(cls, setting: LDTSettings, name: str, parent):
        with setting.group_context(name):
            active = setting.value("active")
            module = importlib.import_module(setting.value("module"))
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
    
    @classmethod
    def loadConfigInItem(cls, item: PluginItem):
        if item.widget is None:
            return
        
        item.widget.load_status(cls.configs.value(item.save_name, LDT()))
    
    @classmethod
    @abstractmethod
    def overCreateItem(
            cls,
            module: ModuleType,
            name_type: str,
            checked: bool = False,
    ) -> PluginItem:
        item = PluginItem(module=module, active=checked, module_type=name_type)
        item.plugin_name = module.__name__
        return item
    
    @classmethod
    @abstractmethod
    def overSaved(cls, item: PluginItem, setting: LDTSettings):
        pass
    
    @classmethod
    @abstractmethod
    def overLoaded(cls, setting: LDTSettings, name: str, parent) -> APIBaseWidget:
        pass
    
    @classmethod
    @abstractmethod
    def getParameterCreateItem(cls, setting: LDTSettings, name: str, parent):
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
        act_reload_c = menu.addAction("Reload Config")
        act_reload_c.triggered.connect(widget.reload_config)
        act_settings = menu.addAction("Setting")
        
        return {"settings": act_settings}
    
    def __init_subclass__(cls, **kwargs):
        if "type" not in kwargs: return
        cls.instances[kwargs.get("type")] = cls
        
    @classmethod
    def clear(cls, setting: LDTSettings):
        for name in cls.instances.keys():
            setting.remove(f"{name}s")
    
    @classmethod
    def save(cls, item: PluginItem, setting: LDTSettings):
        preloader: PreLoader = cls.instances[item.module_type.lower()]
        with setting.group_context(f"{item.module_type.lower()}s"):
            try:
                preloader.saved(item.widget, item, setting)
            except Exception as e:
                qWarning(f"Error {type(e)}: {e}")
    
    @classmethod
    def createMenu(cls, menu: QMenu, widget, item: PluginItem):
        preloader: PreLoader = cls.instances[item.module_type.lower()]
        return preloader.createActionMenu(menu, widget, item)
