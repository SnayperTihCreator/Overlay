from pydantic.dataclasses import dataclass

from .common_config import CommonConfig


@dataclass
class Platform:
    platform: str
    window: str


class OAddonsConfig(CommonConfig):
    platform: Platform
