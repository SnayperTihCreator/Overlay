from contextlib import contextmanager

from PySide6.QtCore import QSettings

from Service.pluginItems import PluginItem
from API import DraggableWindow, OverlayWidget
from APIService.dumper import Dumper


class PluginControl:
    @classmethod
    def saveConfig(cls, item: PluginItem, settings: QSettings):
        dumper = cls.getDumper(item.typeModule)
        with cls.enterGroup(settings, f"{item.typeModule.lower()}s"):
            dumper.saved(item.widget, item, settings)
    
    @classmethod
    @contextmanager
    def enterGroup(cls, settings: QSettings, group):
        settings.beginGroup(group)
        yield
        settings.endGroup()
    
    @staticmethod
    def getObjectWithType(objs, type_name, name):
        name_group = f"{type_name.lower()}s"
        return objs[name_group].get(name, None)
    
    @staticmethod
    def getDumper(type_name) -> Dumper:
        match type_name:
            case "Window":
                return DraggableWindow.dumper
            case "Widget":
                return OverlayWidget.dumper
