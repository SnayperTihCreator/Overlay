import enum

from fs.base import FS
from fs.opener import registry
from fs.opener.parse import ParseResult
from fs.osfs import OSFS
from fs import errors, path as fs_path

from .fs_base import ZipFormatFile, MyWrapReadOnly, BasePathOpener


class PluginFS(ZipFormatFile):
    suffix_file = "plugin"
    
    def __init__(self):
        super().__init__(str(global_cxt.pluginPath))


class PluginDataFS(OSFS):
    def __init__(self):
        global_cxt.pluginDataPath.mkdir(exist_ok=True)
        super().__init__(str(global_cxt.pluginDataPath), True)


class ProjectFS(OSFS):
    def __init__(self):
        super().__init__(str(global_cxt.appPath))


class ThemeFS(ZipFormatFile):
    suffix_file = "overtheme"
    
    def __init__(self):
        super().__init__(str(global_cxt.resourcePath))


class ResourceFS(ZipFormatFile):
    suffix_file = "resource"
    
    def __init__(self):
        super().__init__(str(global_cxt.resourcePath))


class OverlayAddonsFS(ZipFormatFile):
    suffix_file = "oaddons"
    
    def __init__(self, create=False):
        super().__init__(str(global_cxt.resourcePath), create=create)


@registry.install
class PluginPathOpener(BasePathOpener):
    protocols = ["plugin"]
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        return MyWrapReadOnly(PluginFS())


@registry.install
class PluginDataPathOpener(BasePathOpener):
    protocols = ["pldata"]
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        return PluginDataFS()


@registry.install
class ProjectPathOpener(BasePathOpener):
    protocols = ["project"]
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        return ProjectFS()


@registry.install
class ResourcePathOpener(BasePathOpener):
    protocols = ["resource"]
    
    class TypeResource(enum.StrEnum):
        TYPE_NOT_TYPE = "NOT_TYPE"
        TYPE_THEME = "theme"
        TYPE_RESOURCE = "resource"
        TYPE_OVERLAY_ADDONS = "overlay_addons"
    
    def __init__(self):
        self.typeResource = self.TypeResource.TYPE_NOT_TYPE
    
    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str) -> FS:
        path: str = parse_result.resource
        parts = fs_path.parts(path)
        if parts[1].lower() == "NOT_TYPE":
            raise errors.ResourceNotFound(path)
        try:
            self.TypeResource(parts[1].lower())
        except ValueError as e:
            raise errors.ResourceNotFound(path, e)
        self.typeResource = self.TypeResource(parts[1].lower())
        parts.pop(1)
        result = ParseResult(
            parse_result.protocol,
            parse_result.username,
            parse_result.password,
            fs_path.join(*parts),
            parse_result.params,
            parse_result.path
        )
        return super().open_fs(fs_url, result, writeable, create, cwd)
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        match self.typeResource:
            case self.TypeResource.TYPE_THEME:
                return MyWrapReadOnly(ThemeFS())
            case self.TypeResource.TYPE_RESOURCE:
                return MyWrapReadOnly(ResourceFS())
            case self.TypeResource.TYPE_OVERLAY_ADDONS:
                return MyWrapReadOnly(OverlayAddonsFS(create))
