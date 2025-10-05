import importlib
from types import ModuleType
from abc import ABC, abstractmethod, ABCMeta

from PySide6.QtCore import QSettings, qWarning
from PySide6.QtWidgets import QMenu
import json5

from .pluginItems import PluginItem
from Common.core import APIBaseWidget


class MetaSingToolsPreloader(ABCMeta):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class PreLoader(ABC, metaclass=MetaSingToolsPreloader):
    instances = {}
    configs = {}
    
    @classmethod
    def loadConfigs(cls):
        cls.configs.clear()
        with open("project://configs/configs_plugins.json5") as configs_file:
            cls.configs |= json5.load(configs_file)
    
    @classmethod
    def saveConfigs(cls):
        with open("project://configs/configs_plugins.json5", "w") as configs_file:
            json5.dump(cls.configs, configs_file, ensure_ascii=False, indent=4)
    
    @classmethod
    def saved(cls, target: APIBaseWidget, item: PluginItem, setting: QSettings):
        try:
            setting.beginGroup(item.save_name)
            if target is not None:
                config = target.save_config().model_dump(mode="json")
                cls.configs[item.save_name] = config
            setting.setValue("module", item.module.__name__)
            setting.setValue("active", int(item.active))
            setting.setValue("orig_name", item.namePlugin)
            cls.overSaved(item, setting)
        finally:
            setting.endGroup()
    
    @classmethod
    def loaded(cls, setting: QSettings, name: str, parent):
        try:
            setting.beginGroup(name)
            active = bool(int(setting.value("active")))
            module = importlib.import_module(setting.value("module"))
            origname = setting.value("orig_name", name.rsplit("_", 1)[0])
            parameters = [
                module,
                active,
                *cls.getParameterCreateItem(setting, name, parent),
            ]
            item = cls.overCreateItem(*parameters)
            item.namePlugin = origname
            
            target = cls.overLoaded(setting, name, parent)
            
            if active:
                target = item.build(parent)
                cls.loadConfigInItem(item)
                cls.activatedWidget(active, target)
        finally:
            setting.endGroup()
        return target, item
    
    @classmethod
    def loadConfigInItem(cls, item: PluginItem):
        if item.widget is None:
            return
        
        config = cls.configs.get(item.save_name, {})
        item.widget.restore_config(config)
    
    @classmethod
    @abstractmethod
    def overCreateItem(
            cls,
            module: ModuleType,
            name_type: str,
            checked: bool = False,
    ) -> PluginItem:
        item = PluginItem(module, name_type, checked)
        return item
    
    @classmethod
    @abstractmethod
    def overSaved(cls, item: PluginItem, setting: QSettings):
        pass
    
    @classmethod
    @abstractmethod
    def overLoaded(cls, setting: QSettings, name: str, parent) -> APIBaseWidget:
        pass
    
    @classmethod
    @abstractmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent):
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
    def createActionMenu(cls, menu: QMenu, widget, item: PluginItem):
        act_reload_c = menu.addAction("Reload Config")
        act_reload_c.triggered.connect(widget.reloadConfig)
        act_settings = menu.addAction("Setting")
        
        return {"settings": act_settings}
    
    def __init_subclass__(cls, **kwargs):
        if "type" not in kwargs: return
        cls.instances[kwargs.get("type")] = cls
    
    @classmethod
    def save(cls, item: PluginItem, setting: QSettings):
        preloader: PreLoader = cls.instances[item.typeModule.lower()]
        try:
            setting.beginGroup(f"{item.typeModule.lower()}s")
            preloader.saved(item.widget, item, setting)
        except Exception as e:
            qWarning(f"Error {type(e)}: {e}")
        finally:
            setting.endGroup()
    
    @classmethod
    def createMenu(cls, menu: QMenu, widget, item: PluginItem):
        preloader: PreLoader = cls.instances[item.typeModule.lower()]
        return preloader.createActionMenu(menu, widget, item)
