import re
from abc import ABC, abstractmethod
from functools import cached_property

from pydantic import BaseModel, Field
from attrs import define, field
from toml import loads

version_pattern = re.compile(r"(?P<ver>alpha|beta|release)"
                             r" (?P<v1>\d+)\.(?P<v2>\d+)\.(?P<v3>\d+)(?:\s?-\s?"
                             r"(?P<state>unstable|stable))?", re.I)
version_type = ["alpha", "beta", "release"]
version_state = ["unstable", "stable"]


class BaseMetaData(BaseModel):
    author: str = Field("<unknown>")
    description: str = Field("<no description>")
    version: str = Field(..., pattern=version_pattern)
    
    @classmethod
    def from_toml(cls, toml_data: str):
        return cls(**loads(toml_data))
    
    def tuple_version(self):
        dv = self.dict_version()
        return (version_type.index(dv["ver"].lower()),
                int(dv["v1"]), int(dv["v2"]), int(dv["v3"]),
                version_state.index(dv["state"].lower()))
    
    def dict_version(self):
        return version_pattern.fullmatch(self.version).groupdict()


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
