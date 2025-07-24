from types import ModuleType
from typing import Type

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QListWidgetItem, QMenu

from APIService.dumper import Dumper

from Service.core import ItemRole
from Service.pluginItems import PluginItem


class DraggableWindowDumper(Dumper):
    
    @classmethod
    def overCreateItem(
        cls,
        module: ModuleType,
        name: str,
        parent,
        checked: bool = False,
        count_dup: int = 0,
        is_dup: bool = False,
    ):
        item: PluginItem = super().overCreateItem(module, name, "Window", parent, checked)
        item.countClone = count_dup
        item.isDuplication = is_dup
        return item

    @classmethod
    def overRunFunction(cls, module: ModuleType, parent):
        return module.createWindow(parent)

    @classmethod
    def overSaved(cls, item: QListWidgetItem, setting: QSettings):
        setting.setValue("count_dub", item.data(ItemRole.COUNT_DUPLICATE))
        setting.setValue("is_dub", int(item.data(ItemRole.IS_DUPLICATE)))

    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent):
        return None

    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent):
        return int(setting.value("count_dub")), bool(int(setting.value("is_dub")))

    @classmethod
    def activatedWidget(cls, state, target):
        if state == Qt.CheckState.Checked:
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
        
        if item.isDuplication:
            act_delete_d = menu.addAction("Delete duplicate")
            actions |= {"delete_duplicate": act_delete_d}

        return actions
