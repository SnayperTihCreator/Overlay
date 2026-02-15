from abc import ABC, abstractmethod
from functools import cached_property
import logging

from attrs import define, field

from core.default_configs import MetaData

logger = logging.getLogger(__name__)


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
                    try:
                        return ParseName(*self._conversion_table_[name])
                    except KeyError:
                        logger.warning(f"Metadata alias not found: '{name}'")
                        return ParseName(name, "unknown")
                
                case [_type, name]:
                    return ParseName(name, _type)
                case _:
                    logger.warning(f"Invalid metadata path format: '{path}'")
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
