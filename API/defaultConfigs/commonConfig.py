from dataclasses import field

from pydantic.dataclasses import dataclass
from pydantic import Field, BaseModel, ConfigDict


@dataclass(frozen=True)
class Ports:
    begin: int = Field(ge=1024, le=49151)
    end: int = Field(ge=1024, le=49151)


@dataclass(frozen=True)
class ChapterInfoCreator:
    author: str = field(default="<unknown>")


@dataclass(frozen=True)
class ChapterNameResource(ChapterInfoCreator):
    name: str = field(default="<unknown>")


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )