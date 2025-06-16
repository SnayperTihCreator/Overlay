from types import ModuleType

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QListWidgetItem, QMenu

from utils import Dumper

from Service.core import ItemRole


class WorkerDumper(Dumper):
    @classmethod
    def overCreateItem(
        cls,
        module: ModuleType,
        name: str,
        checked: Qt.CheckState = Qt.CheckState.Unchecked,
    ):
        return super().overCreateItem(module, name, checked)

    @classmethod
    def overRunFunction(cls, module: ModuleType, parent):
        return module.createWidget(parent)

    @classmethod
    def overSaved(cls, item: QListWidgetItem, setting: QSettings):
        return None

    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent):
        return None

    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent):
        return []

    @classmethod
    def activatedWidget(cls, state, target):
        if state == Qt.CheckState.Checked:
            target.show()
        else:
            target.hide()

    @classmethod
    def duplicate(cls, item: QListWidgetItem):
        return NotImplemented

    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: QListWidgetItem):
        return super().createActionMenu(menu, widget, item)
