from dataclasses import field

from pydantic.dataclasses import dataclass
from pydantic import Field

from .commonConfig import Ports, BaseConfig


@dataclass(frozen=True)
class ChapterWebSockets:
    IN: Ports = field(default=Ports(8000, 8010))
    OUT: Ports = field(default=Ports(8015, 8020))


@dataclass(frozen=True)
class ChapterShortKey:
    open: str = field(default="shift+alt+o")


class ConfigApps(BaseConfig):
    websockets: ChapterWebSockets = Field(default_factory=ChapterWebSockets)
    shortkey: ChapterShortKey = Field(default_factory=ChapterShortKey)
