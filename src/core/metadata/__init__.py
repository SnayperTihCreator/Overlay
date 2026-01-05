from typing import Any

from core.default_configs import MetaData
from .model import MetaDataFinder

_meta_finders: list[MetaDataFinder] = []


def registry(cls=None, **kwargs):
    def wrapper(finder):
        if not issubclass(finder, MetaDataFinder):
            raise TypeError(f"{finder} it is not inherited from MetaDataFinder")
        _meta_finders.append(finder(**kwargs))
        return finder
    
    if cls is None:
        return wrapper
    
    return wrapper(cls)


def metadata(path: str) -> MetaData:
    for finder in _meta_finders:
        context = finder.Context(path, finder.getTable())
        md = finder.find_metadata(context)
        if md is not None:
            return md
    raise ValueError(f"metadata not find for {path}")


def version(path: str) -> Any:
    meta = metadata(path)
    return meta.version
