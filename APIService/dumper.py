import importlib
from types import ModuleType
from abc import ABC, abstractmethod

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QListWidgetItem, QMenu
from PySide6.QtGui import QPixmap
import json5
from box import Box

from Service.core import ItemRole
from APIService.path_controls import PluginPath


class Dumper(ABC):
    @classmethod
    def saved(cls, target, item: QListWidgetItem, setting: QSettings):
        setting.beginGroup(item.text())
        if target is not None:
            setting.setValue(
                "config", json5.dumps(target.savesConfig(), ensure_ascii=False)
            )
        else:
            setting.setValue("config", "{}")
        setting.setValue("has_init", int(target is not None))
        setting.setValue("module", item.data(ItemRole.MODULE).__name__)
        setting.setValue("active", int(item.checkState() == Qt.CheckState.Checked))
        cls.overSaved(item, setting)
        setting.endGroup()

    @classmethod
    def loaded(cls, setting: QSettings, name: str, parent):
        setting.beginGroup(name)
        config = json5.loads(setting.value("config")) if setting.value("config") else {}
        active = getattr(
            Qt.CheckState, ("Checked" if int(setting.value("active")) else "Unchecked")
        )
        has_init = int(setting.value("has_init"))
        module = importlib.import_module(setting.value("module"))
        parameters = [
            module,
            name,
            active,
            *cls.getParameterCreateItem(setting, name, parent),
        ]
        item = cls.overCreateItem(*parameters)

        target = cls.overLoaded(setting, name, parent)

        if has_init:
            target = cls.overRunFunction(module, parent)
            target.restoreConfig(Box(config, default_box=True))
            cls.activatedWidget(active, target)
        setting.endGroup()
        return target, item
    
    @classmethod
    def getIcon(cls, name):
        path = PluginPath(name)
        result = QPixmap()
        try:
            image_data = path.open("plugin:/icon.png", "rb").read()
            result.loadFromData(image_data)
        except FileNotFoundError as e:
            print(e, name, path)
        return result

    @classmethod
    @abstractmethod
    def overCreateItem(
        cls,
            module: ModuleType,
            name: str,
            name_type: str,
            checked: Qt.CheckState = Qt.CheckState.Unchecked,
    ) -> QListWidgetItem:
        icon_name = name
        if f"({name_type})" not in name:
            name = f"{name}({name_type})"
        if f"({name_type})" in icon_name:
            icon_name = icon_name[:icon_name.rindex("(")]
        icon = cls.getIcon(icon_name)
        item = QListWidgetItem(icon, name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(checked)
        item.setData(ItemRole.MODULE, module)
        item.setData(ItemRole.TYPE_NAME, name_type)
        return item

    @classmethod
    @abstractmethod
    def overRunFunction(cls, module: ModuleType, parent):
        pass

    @classmethod
    @abstractmethod
    def overSaved(cls, item: QListWidgetItem, setting: QSettings):
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
    def duplicate(cls, item: QListWidgetItem):
        item.setData(ItemRole.COUNT_DUPLICATE, item.data(ItemRole.COUNT_DUPLICATE) + 1)
        d_item = QListWidgetItem(
            f"{item.text()}_{item.data(ItemRole.COUNT_DUPLICATE):04d}"
        )
        d_item.setIcon(item.icon())
        d_item.setData(ItemRole.TYPE_NAME, item.data(ItemRole.TYPE_NAME))
        d_item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        d_item.setCheckState(Qt.CheckState.Unchecked)
        d_item.setData(ItemRole.MODULE, item.data(ItemRole.MODULE))
        return d_item

    @classmethod
    @abstractmethod
    def createActionMenu(cls, menu: QMenu, widget, item: QListWidgetItem):
        act_reload_c = menu.addAction("Reload Config")
        act_reload_c.triggered.connect(widget.reloadConfig)
        act_settings = menu.addAction("Setting")

        return {"settings": act_settings}
