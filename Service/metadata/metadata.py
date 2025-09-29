import re
from abc import ABC, abstractmethod
from functools import cached_property

from pydantic import BaseModel, Field
from attrs import define, field
from toml import loads

version_pattern = re.compile(r"alpha|beta|release"
                             r" \d+\.\d+\.\d+(?: - "
                             r"unstable|stable)?", re.I)


class BaseMetaData(BaseModel):
    author: str = Field("<unknown>")
    description: str = Field("<no description>")
    version: str = Field(..., pattern=version_pattern)
    
    @classmethod
    def from_toml(cls, toml_data: str):
        return cls(**loads(toml_data))


@define(frozen=True, hash=True, order=True)
class ParseName:
    name: str = field()
    type: str = field()


class MetaDataFinder(ABC):
    @define(frozen=True, hash=True, order=True)
    class Context:
        path: str = field()
        _conversion_table_: dict = field()
        
        def _parseName(self, path) -> ParseName:
            match path.split("::"):
                case [name]:
                    return ParseName(*self._conversion_table_[name])
                case [_type, name]:
                    return ParseName(name, _type)
                case _:
                    return ParseName("", "")
        
        @cached_property
        def name(self):
            return self._parseName(self.path).name
        
        @cached_property
        def type(self):
            return self._parseName(self.path).type
    
    _conversion_table_: dict[str, tuple[str, str]] = {}
    
    def __init__(self, **kwargs):
        ...
    
    @abstractmethod
    def find_metadata(self, context: "MetaDataFinder.Context"):
        ...
