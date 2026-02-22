import logging
import builtins
from attrs import define, field
from pathlib import Path
from utils.fs import getAppPath

# Setup logger
logger = logging.getLogger(__name__)


class MetaSingTools(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.debug(f"Creating singleton {cls.__name__}")
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


@define(frozen=True)
class GlobalContext(metaclass=MetaSingTools):
    appPath: Path = field(factory=lambda: getAppPath())
    pluginPath: Path = field(factory=lambda: getAppPath() / "plugins")
    pluginDataPath: Path = field(factory=lambda: getAppPath() / "plugins" / "plugin_data")
    toolsPath: Path = field(factory=lambda: getAppPath() / "tools")
    resourcePath: Path = field(factory=lambda: getAppPath() / "resource")
    
    def __attrs_post_init__(self):
        logger.info(f"GlobalContext initialized. Base path: {self.appPath}")


def registryGlobalContext():
    try:
        builtins.global_cxt = GlobalContext()
        logger.info("GlobalContext registered to builtins.")
    except Exception as e:
        logger.critical(f"Failed to register GlobalContext! {e}", exc_info=True)
        raise e


def cleanupGlobalContext():
    try:
        if hasattr(builtins, "global_cxt"):
            del builtins.global_cxt
            logger.info("GlobalContext cleaned up.")
    except Exception as e:
        logger.warning(f"Error during GlobalContext cleanup: {e}")


registryGlobalContext()
