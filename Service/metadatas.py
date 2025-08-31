import importlib.metadata as metadata
from collections import defaultdict
from typing import Any, Sequence
from functools import cached_property

import toml
from attrs import field, define, Converter


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
        return self._data.get(key, set()).copy()
    
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
    _data: MultiDict | Sequence[tuple[str, Any]] = field(default=MultiDict, converter=Converter(lambda x: MultiDict(x)))
    
    def __len__(self):
        return len(self._data)
    
    def __contains__(self, item):
        return item in self._data
    
    def __getitem__(self, item):
        return self._data.__getitem__(item).pop()
    
    def __iter__(self):
        return self._data.__iter__()
    
    def get_all(self, name, failobj=...):
        data = self._data[name]
        if data:
            return list(data)
        return failobj
    
    @property
    def json(self):
        return dict(self._data)


@define
class OverlayDistribution(metadata.Distribution):
    _name: str = field()
    _type: str = field()
    
    def locate_file(self, path):
        pass
    
    def read_text(self, filename):
        return open(filename, encoding="utf-8").read()
    
    @cached_property
    def metadata(self):
        data = {}
        match self._type:
            case "plugins":
                data = toml.loads(self.read_text(f"plugin://{self._name}/metadata.toml"))
            case "apps":
                data = toml.loads(self.read_text(f"qt://app/metadata.toml"))
            case "theme":
                data = toml.loads(self.read_text(f"resource://theme/{self._name}/config.toml"))
        return MetaData(list(data.items()))
    
    @property
    def version(self):
        return self.metadata["version"]
    
    @property
    def name(self):
        return self.metadata["name"]
    
    @property
    def entry_points(self):
        return metadata.EntryPoints()


class OverlayDistributionFinder(metadata.DistributionFinder):
    
    def find_distributions(self, context: metadata.DistributionFinder.Context = ...):
        if context.name is None: return
        match context.name.split("::"):
            case ["Overlay", "App"]:
                yield OverlayDistribution("overlay", "apps")
            case ["Overlay", "plugins", plugin]:
                yield OverlayDistribution(plugin, "plugin")
            case ["Overlay", "theme", theme]:
                yield OverlayDistribution(theme, "theme")
            case _:
                return


import sys

sys.meta_path.insert(0, OverlayDistributionFinder())
