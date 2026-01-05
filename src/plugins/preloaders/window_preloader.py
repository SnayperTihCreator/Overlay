from types import ModuleType

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu

from .preloader import PreLoader
from plugins.items import PluginItem


class WindowPreLoader(PreLoader, type="window"):
    
    @classmethod
    def overCreateItem(
            cls,
            module: ModuleType,
            checked: bool = False,
            count_dup: int = 0,
            is_dup: bool = False,
    ):
        item: PluginItem = super().overCreateItem(module, "Window", checked)
        item.clone_count = count_dup
        item.is_duplicate = is_dup
        
        return item
    
    @classmethod
    def overSaved(cls, item: PluginItem, setting: QSettings):
        setting.setValue("clone_count", item.clone_count)
        setting.setValue("is_duplicate", item.is_duplicate)
    
    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent):
        return None
    
    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent):
        return setting.value("clone_count", 0), setting.value("is_duplicate", False)
    
    @classmethod
    def activatedWidget(cls, state, target):
        if state:
            target.ready()
            target.show()
        else:
            target.hide()
    
    @classmethod
    def duplicate(cls, item: PluginItem):
        return item.clone()
    
    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: PluginItem):
        actions = super().createActionMenu(menu, widget, item)
        act_highlight_b = menu.addAction("Highlight Border")
        act_highlight_b.triggered.connect(widget.highlightBorder)
        
        act_duplicate = menu.addAction("Duplicate")
        actions |= {"duplicate": act_duplicate}
        
        if item.is_duplicate:
            act_delete_d = menu.addAction("Delete duplicate")
            actions |= {"delete_duplicate": act_delete_d}
        
        return actions
