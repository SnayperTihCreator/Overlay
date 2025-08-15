from types import ModuleType

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu

from ApiPlugins.preloader import PreLoader
from ApiPlugins.pluginItems import PluginItem


class WidgetPreLoader(PreLoader):
    @classmethod
    def overCreateItem(cls, module: ModuleType, checked: bool = False, **kwargs):
        return super().overCreateItem(module, "Widget", checked)

    @classmethod
    def overRunFunction(cls, module: ModuleType, parent):
        return module.createWidget(parent)

    @classmethod
    def overSaved(cls, item: PluginItem, setting: QSettings):
        return None

    @classmethod
    def overLoaded(cls, setting: QSettings, name: str, parent):
        return None

    @classmethod
    def getParameterCreateItem(cls, setting: QSettings, name: str, parent):
        return []

    @classmethod
    def activatedWidget(cls, state, target):
        if state:
            target.loader()
            target.show()
        else:
            target.hide()

    @classmethod
    def duplicate(cls, item: PluginItem):
        return NotImplemented

    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: PluginItem):
        return super().createActionMenu(menu, widget, item)
