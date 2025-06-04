from types import ModuleType

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QListWidgetItem, QMenu, QWidget

from utils import Dumper

from core import ItemRole


class DraggableWindowDumper(Dumper):
    @classmethod
    def overCreateItem(
        cls,
        module: ModuleType,
        name: str,
        checked: Qt.CheckState = Qt.CheckState.Unchecked,
        count_dup: int = 0,
        is_dup: bool = False,
    ):
        item = super().overCreateItem(module, name, "Window", checked)
        item.setData(ItemRole.IS_DUPLICATE, is_dup)
        item.setData(ItemRole.COUNT_DUPLICATE, count_dup)
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
    def duplicate(cls, item: QListWidgetItem):
        d_item = super().duplicate(item)
        d_item.setData(ItemRole.COUNT_DUPLICATE, 0)
        d_item.setData(ItemRole.IS_DUPLICATE, True)
        return d_item

    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: QListWidgetItem):
        actions = super().createActionMenu(menu, widget, item)
        act_highlight_b = menu.addAction("Highlight Border")
        act_highlight_b.triggered.connect(widget.highlightBorder)
        
        act_duplicate = menu.addAction("Duplicate")
        actions |= {"duplicate": act_duplicate}
        if item.data(ItemRole.IS_DUPLICATE):
            act_delete_d = menu.addAction("Delete duplicate")
            actions |= {"delete_duplicate": act_delete_d}

        return actions
