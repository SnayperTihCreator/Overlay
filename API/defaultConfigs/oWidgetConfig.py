from dataclasses import field

from pydantic.dataclasses import dataclass
from pydantic import Field

from .commonConfig import BaseConfig


@dataclass
class ChapterWidget:
    styleFile: str = field(default="style.css")


class ConfigWidget(BaseConfig):
    widget: ChapterWidget = Field(default_factory=ChapterWidget)
