import importlib.metadata as metadata
from typing import Any
from collections import defaultdict
import json

from attrs import define, field, Converter


@define(repr=False, init=False)
class MultiDict:
    _data: defaultdict[Any, set] = field(factory=lambda: defaultdict(set))
    
    def __init__(self, args):
        # noinspection PyUnresolvedReferences
        self.__attrs_init__()
        for k, v in args:
            self[k] = v
    
    def __setitem__(self, key, value):
        self._data[key].add(value)
    
    def __len__(self):
        return len(self.keys())
    
    def __getitem__(self, key):
        return self._data.get(key, set())
    
    def __delitem__(self, key):
        if key not in self._data: return
        self._data[key].pop()
        if not self._data[key]:
            del self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def items(self):
        for k, items in self._data.items():
            for item in items:
                yield k, item
    
    def __iter__(self):
        return self.keys()
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        for items in self._data.values():
            for item in items:
                yield item
    
    def __repr__(self):
        return f"""MultiDict({", ".join(f"{k!r}:{v!r}" for k, v in self.items())})"""


@define
class MetaData:
    _data: MultiDict | list[tuple[str, Any]] = field(default=MultiDict, converter=Converter(lambda x: MultiDict(x)))
    
    def __len__(self):
        return len(self._data)
    
    def __contains__(self, item):
        return item in self._data
    
    def __getitem__(self, item):
        return self._data.__getitem__(item)
    
    def __iter__(self):
        return self._data.__iter__()
    
    def get_all(self, name, failobj=...):
        data = self._data[name]
        if data:
            return
        return failobj
    
    @property
    def json(self):
        return dict(self._data)


class TestDistribution(metadata.Distribution):
    
    def locate_file(self, path):
        pass
    
    @property
    def name(self):
        return super().name
    
    @property
    def requires(self):
        return super().requires
    
    @property
    def files(self):
        return super().files
    
    @property
    def version(self):
        return super().version
    
    @property
    def metadata(self):
        return super().metadata
    
    def read_text(self, filename):
        pass


class TestFinder(metadata.DistributionFinder):
    
    def find_distributions(self, context: metadata.DistributionFinder.Context = ...):
        print(context.name)
        yield None
        
        
import sys
sys.meta_path.insert(0, TestFinder())


if __name__ == '__main__':
    a = MetaData([("a", 5), ("a", 7)])
    
    metadata.version("Overlay")
