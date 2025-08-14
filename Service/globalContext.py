from attrs import define, field
from pathlib import Path
from PathControl import getAppPath


class MetaSingTools(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


@define(frozen=True)
class GlobalContext(metaclass=MetaSingTools):
    appPath: Path = field(default=getAppPath())
    pluginPath: Path = field(default=getAppPath() / "plugins")
    pluginDataPath: Path = field(default=getAppPath()/"plugins"/"plugin_data")
    toolsPath: Path = field(default=getAppPath()/"tools")
    resourcePath: Path = field(default=getAppPath()/"resource")


def registryGlobalContext():
    import builtins
    builtins.global_cxt = GlobalContext()


def cleanupGlobalContext():
    import builtins
    del builtins.global_cxt

registryGlobalContext()