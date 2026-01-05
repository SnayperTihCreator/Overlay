from typing import Optional

from pydantic.dataclasses import dataclass
from pydantic import Field

from .common_config import CommonConfig


@dataclass
class WindowSettings:
    width: int
    height: int
    opacity: float = Field(ge=0.0, le=1.0)


@dataclass
class WidgetSettings:
    ...


@dataclass
class Settings:
    style_file: str
    window: Optional[WindowSettings] = Field(None)
    widget: Optional[WidgetSettings] = Field(None)


class PluginConfig(CommonConfig):
    settings: Settings
