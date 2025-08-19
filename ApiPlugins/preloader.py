import importlib
from types import ModuleType
from abc import ABC, abstractmethod

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu
import json5
from box import Box

from ApiPlugins.pluginItems import PluginItem


class PreLoader(ABC):
    @classmethod
    def saved(cls, target, item: PluginItem, setting: QSettings):
        setting.beginGroup(item.save_name)
        if target is not None:
            setting.setValue(
                "config", json5.dumps(target.savesConfig(), ensure_ascii=False)
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
            target.restoreConfig(Box(config, default_box=True))
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
    def overLoaded(cls, setting: QSettings, name: str, parent):
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
