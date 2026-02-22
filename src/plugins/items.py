import logging
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from functools import cached_property
from methodtools import lru_cache
from types import ModuleType
from typing import Optional, Literal, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStyle, QApplication
from PySide6.QtGui import QPixmap
from attrs import define, field

from core.errors import PluginBuild
from core.common import APIBaseWidget
from gui.themes import ThemeController

# Initialize logger for this module
logger = logging.getLogger(__name__)


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
    """Abstract plugin interface with frozen base properties."""
    plugin_name: str = field(default=None, init=False)
    is_bad: bool = field(default=False, init=False)
    
    @property
    @abstractmethod
    def icon(self):
        """Method to get the icon, specific to the plugin state."""
        pass
    
    @abstractmethod
    def build(self, parent: QWidget) -> APIBaseWidget:
        pass


@define(slots=False, kw_only=True)
class PluginItem(PluginBase):
    module: ModuleType = field(repr=False)
    module_type: Literal["Window", "Widget"] = field()
    active: bool = field(default=False)
    
    # Auxiliary fields for cloning
    clone_count: int = field(init=False, default=0, repr=False)
    is_duplicate: bool = field(init=False, default=False, repr=False)
    widget: Optional[APIBaseWidget] = field(init=False, default=None, repr=False)
    
    def __attrs_post_init__(self):
        try:
            self.plugin_name = self.module.__name__
        except Exception as e:
            logger.error(f"Failed to set plugin name from module: {e}", exc_info=True)
            self.plugin_name = "UnknownPlugin"
    
    @property
    def icon(self):
        """Proxy that takes the actual theme name."""
        try:
            theme_name = ThemeController().themeName()
            return self._get_cached_icon(theme_name)
        except Exception as e:
            logger.error(f"Failed to retrieve icon for {self.plugin_name}: {e}", exc_info=True)
            return QPixmap()
    
    @lru_cache(maxsize=3)
    def _get_cached_icon(self, _):
        """
        Internal method. Thanks to lru_cache, if theme_name hasn't changed,
        the method body is not executed.
        """
        try:
            icon_path = f"plugin://{self.module.__name__}/icon.png"
            return ThemeController().getImage(icon_path)
        except Exception as e:
            logger.error(f"Failed to load cached icon: {e}", exc_info=True)
            return QPixmap()
    
    @cached_property
    def save_name(self) -> str:
        return f"{self.plugin_name}_{self.module_type}"
    
    # noinspection PyDunderSlots,PyUnresolvedReferences
    def build(self, parent: QWidget) -> Optional[APIBaseWidget]:
        try:
            if self.widget is None:
                creator_name = f"create{self.module_type}"
                builder = getattr(self.module, creator_name, None)
                
                if builder:
                    logger.debug(f"Building plugin '{self.plugin_name}' using {creator_name}")
                    self.widget = builder(parent)
                else:
                    error_msg = f"Module {self.plugin_name} has no creator for {self.module_type}"
                    logger.error(error_msg)
                    raise AttributeError(error_msg)
            return self.widget
        except Exception as e:
            logger.error(f"Failed to build plugin '{self.plugin_name}': {e}", exc_info=True)
            return None
    
    def clone(self) -> "PluginItem":
        try:
            self.clone_count += 1
            item = PluginItem(
                module=self.module,
                module_type=self.module_type
            )
            item.is_duplicate = True
            item.plugin_name = f"{self.plugin_name}_{self.clone_count:04d}"
            return item
        except Exception as e:
            logger.error(f"Failed to clone plugin item: {e}", exc_info=True)
            # Return self in worst case to avoid NoneType errors upstream, 
            # though this might mask logic errors.
            return self


@define(frozen=True, slots=False, kw_only=True)
class PluginBadItem(PluginBase):
    plugin_name = field()
    is_bad: bool = field(init=False, default=True)
    error: Exception | None = field(default=None)
    module_type: str = field(default="bad_element", init=False, repr=False)
    
    @property
    def icon(self):
        try:
            return QApplication.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning)
        except Exception as e:
            logger.error(f"Failed to get standard warning icon: {e}", exc_info=True)
            return QPixmap()
    
    def build(self, parent):
        logger.warning(f"Attempted to build bad plugin: {self.plugin_name}")
        raise PluginBuild(self.plugin_name)
    
    def show_info(self):
        logger.warning(f"Plugin error '{self.plugin_name}': {self.error}")
        if self.error:
            logger.debug(f"Detailed error for {self.plugin_name}: {self.error}", exc_info=True)
    
    def getErrorStr(self):
        return f"Error {type(self.error).__name__}: {self.error}"
