from typing import Any
import logging

from core.default_configs import MetaData
from .model import MetaDataFinder

_meta_finders: list[MetaDataFinder] = []

logger = logging.getLogger(__name__)


def registry(cls=None, **kwargs):
    def wrapper(finder):
        if not issubclass(finder, MetaDataFinder):
            msg = f"Class '{finder.__name__}' must inherit from MetaDataFinder"
            logger.critical(msg)
            raise TypeError(msg)
        
        try:
            instance = finder(**kwargs)
            _meta_finders.append(instance)
            logger.info(f"Metadata finder registered: {finder.__name__}")
        except Exception as e:
            logger.error(f"Failed to register finder '{finder.__name__}': {e}", exc_info=True)
            raise e
        
        return finder
    
    if cls is None:
        return wrapper
    
    return wrapper(cls)


def metadata(path: str) -> MetaData:
    logger.debug(f"Searching metadata for: {path}")
    
    for finder in _meta_finders:
        try:
            context = finder.Context(path, finder.getTable())
            md = finder.find_metadata(context)
            if md is not None:
                return md
        
        except Exception as e:
            logger.warning(f"Finder '{type(finder).__name__}' failed for '{path}': {e}")
            logger.debug("Finder traceback:", exc_info=True)
    
    error_msg = f"Metadata not found for: {path}"
    logger.error(error_msg)
    raise ValueError(error_msg)


def version(path: str) -> Any:
    meta = metadata(path)
    return meta.version
