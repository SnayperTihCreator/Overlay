from types import ModuleType

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMenu

from ApiPlugins.preloader import PreLoader
from ApiPlugins.pluginItems import PluginItem


class WidgetPreLoader(PreLoader, type="widget"):
    @classmethod
    def overCreateItem(cls, module: ModuleType, checked: bool = False, **kwargs):
        return super().overCreateItem(module, "Widget", checked)

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
        target.setActive(state)
        if state:
            target.ready()
            target.show()
        else:
            target.hide()

    @classmethod
    def duplicate(cls, item: PluginItem):
        return NotImplemented

    @classmethod
    def createActionMenu(cls, menu: QMenu, widget, item: PluginItem):
        return super().createActionMenu(menu, widget, item)
