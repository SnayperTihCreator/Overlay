from contextlib import contextmanager

from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import QSettings

from Service.core import ItemRole
from API import DraggableWindow, OverlayWidget
from APIService.dumper import Dumper


class PluginControl:
    @classmethod
    def saveConfig(cls, item: QListWidgetItem, settings: QSettings, objs):
        type_name = item.data(ItemRole.TYPE_NAME)
        dumper = cls.getDumper(type_name)
        obj = cls.getObjectWithType(objs, type_name, item.text())
        with cls.enterGroup(settings, f"{type_name.lower()}s"):
            dumper.saved(obj, item, settings)
        
    @classmethod
    @contextmanager
    def enterGroup(cls, settings:QSettings, group):
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
