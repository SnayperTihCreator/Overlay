from typing import Any

from .metadata import MetaDataFinder, BaseMetaData

_meta_finders: list[MetaDataFinder] = []


def registry(cls=None, **kwargs):
    def wrapper(cls):
        if not issubclass(cls, MetaDataFinder): raise TypeError(f"{cls} it is not inherited from MetaDataFinder")
        _meta_finders.append(cls(**kwargs))
        return cls
    
    if cls is None:
        return wrapper
    
    return wrapper(cls)


def metadata(path: str) -> BaseMetaData:
    for finder in _meta_finders:
        context = finder.Context(path, finder._conversion_table_)
        md = finder.find_metadata(context)
        if md is not None:
            return md
    raise ValueError(f"metadata not find for {path}")


def version(path: str) -> Any:
    meta = metadata(path)
    return meta.version
