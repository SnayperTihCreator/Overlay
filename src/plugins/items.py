from abc import ABC, abstractmethod
from enum import IntEnum, auto
from functools import cached_property
from methodtools import lru_cache
from types import ModuleType
from typing import Optional, Literal
from traceback import format_exception

from PySide6.QtCore import Qt, qWarning
from PySide6.QtWidgets import QWidget, QStyle, QApplication
from attrs import define, field

from core.errors import PluginBuild
from core.common import APIBaseWidget
from gui.themes import ThemeController


class PluginItemRole(IntEnum):
    TYPE_ROLE = Qt.ItemDataRole.UserRole
    ACTIVE_ROLE = auto()
    SELF = auto()
    ICON = auto()
    IS_DUPLICATE = auto()
    IS_BAD = auto()
    ERROR = auto()


@define(slots=False, kw_only=True)
class PluginBase(ABC):
    """Абстрактный интерфейс плагина с замороженными базовыми свойствами."""
    plugin_name: str = field(default=None, init=False)
    is_bad: bool = field(default=False, init=False)
    
    @property
    @abstractmethod
    def icon(self):
        """Метод для получения иконки, специфичный для состояния плагина."""
        pass
    
    @abstractmethod
    def build(self, parent: QWidget) -> APIBaseWidget:
        pass


@define(slots=False, kw_only=True)
class PluginItem(PluginBase):
    module: ModuleType = field(repr=False)
    module_type: Literal["Window", "Widget"] = field()
    active: bool = field(default=False)
    
    # Вспомогательные поля для клонирования
    clone_count: int = field(init=False, default=0, repr=False)
    is_duplicate: bool = field(init=False, default=False, repr=False)
    widget: Optional[APIBaseWidget] = field(init=False, default=None, repr=False)
    
    @property
    def icon(self):
        """Прослойка, которая берет актуальное имя темы."""
        theme_name = ThemeController().themeName()
        return self._get_cached_icon(theme_name)
    
    @lru_cache(maxsize=3)
    def _get_cached_icon(self, _):
        """
        Внутренний метод. Благодаря lru_cache, если theme_name не менялся,
        тело метода не выполняется.
        """
        return ThemeController().getImage(f"plugin://{self.module.__name__}/icon.png")
    
    @cached_property
    def save_name(self) -> str:
        return f"{self.plugin_name}_{self.module_type}"
    
    # noinspection PyDunderSlots,PyUnresolvedReferences
    def build(self, parent: QWidget) -> APIBaseWidget:
        if self.widget is None:
            builder = getattr(self.module, f"create{self.module_type}", None)
            if builder:
                self.widget = builder(parent)
            else:
                raise AttributeError(f"Module {self.plugin_name} has no creator for {self.module_type}")
        return self.widget
    
    def clone(self) -> "PluginItem":
        self.clone_count += 1
        item = PluginItem(
            module=self.module,
            module_type=self.module_type
        )
        item.is_duplicate = True
        item.plugin_name = f"{self.plugin_name}_{self.clone_count:04d}"
        return item


@define(frozen=True, slots=False, kw_only=True)
class PluginBadItem(PluginBase):
    plugin_name = field()
    is_bad: bool = field(init=False, default=True)
    error: Exception | None = field(default=None)
    
    @property
    def icon(self):
        return QApplication.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning)
    
    def build(self, parent):
        raise PluginBuild(self.plugin_name)
    
    def show_info(self):
        data_info = "".join(format_exception(self.error))
        qWarning(f"Ошибка плагина {self.plugin_name}:\n {data_info}")
    
    def getErrorStr(self):
        return f"Error {type(self.error).__name__}: {self.error}"
    