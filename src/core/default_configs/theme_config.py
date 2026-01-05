import re

from pydantic.dataclasses import dataclass
from pydantic import Field

from .common_config import CommonConfig

pattern_color = re.compile(r'^#[A-Fa-f0-9]{6}|#[A-Fa-f0-9]{3}$')


@dataclass
class Palette:
    base: str = Field(..., pattern=pattern_color)
    main_text: str = Field(..., pattern=pattern_color)
    alt_text: str = Field(..., pattern=pattern_color)


class ThemeConfig(CommonConfig):
    palette: Palette
