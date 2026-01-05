from abc import ABC, abstractmethod
from functools import cached_property

from attrs import define, field

from core.default_configs import MetaData


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
    def find_metadata(self, context: "MetaDataFinder.Context") -> MetaData:
        ...
    
    @classmethod
    def getTable(cls):
        return cls._conversion_table_.copy()