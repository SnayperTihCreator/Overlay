from dataclasses import field

from pydantic.dataclasses import dataclass
from pydantic import Field

from .commonConfig import BaseConfig


@dataclass
class ChapterWindow:
    width: int = Field(300, gt=0)
    height: int = Field(200, gt=0)
    styleFile: str = field(default="style.css")
    opacity: float = Field(1, ge=0, le=1)


class ConfigWindow(BaseConfig):
    window: ChapterWindow = Field(default_factory=ChapterWindow)
