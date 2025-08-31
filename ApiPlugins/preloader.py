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
    
    @classmethod
    def saved(cls, target: APIBaseWidget, item: PluginItem, setting: QSettings):
        setting.beginGroup(item.save_name)
        if target is not None:
            config = target.save_config().model_dump(mode="json")
            setting.setValue(
                "config", json5.dumps(config, ensure_ascii=False)
            )
        else:
            setting.setValue("config", "{}")
        setting.setValue("has_init", int(target is not None))
        setting.setValue("module", item.module.__name__)
        setting.setValue("active", int(item.active))
        setting.setValue("orig_name", item.namePlugin)
        cls.overSaved(item, setting)
        setting.endGroup()
    
    @classmethod
    def loaded(cls, setting: QSettings, name: str, parent):
        setting.beginGroup(name)
        config = json5.loads(setting.value("config")) if setting.value("config") else {}
        active = bool(int(setting.value("active")))
        has_init = int(setting.value("has_init"))
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
        
        if has_init:
            target = item.build(parent)
            target.restore_config(config)
            cls.activatedWidget(active, target)
        setting.endGroup()
        return target, item
    
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
    