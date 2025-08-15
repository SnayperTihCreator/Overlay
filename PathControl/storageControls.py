import os, io
from contextlib import contextmanager
from contextvars import ContextVar
from os import path as ospath, fsencode
import pathlib
from abc import abstractmethod
from functools import lru_cache, wraps
import re

from fs.base import FS
from fs.opener import Opener, registry
from fs.opener.parse import ParseResult, parse_fs_url
from fs.enums import ResourceType
from fs.osfs import OSFS
from fs.wrap import WrapReadOnly
from fs import errors, open_fs, path as fs_path

_current_plugin = ContextVar("CurrentPlugin", default="App")


def isActiveContextPlugin():
    return _current_plugin.get() != "App"


def innerPlugin(pluginName):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            lastContext = _current_plugin.get()
            _current_plugin.set(pluginName)
            result = func(*args, **kwargs)
            _current_plugin.set(lastContext)
            return result
        
        return inner
    
    return wrapper


def decoPlugin(pluginName):
    def wrapper(cls):
        for name, attr in cls.__dict__.items():  # Используем __dict__ вместо vars
            if callable(attr) and not name.startswith('__'):
                setattr(cls, name, innerPlugin(pluginName)(attr))
            
            # Обрабатываем наследование
        for base in cls.__bases__:
            for name, attr in base.__dict__.items():
                if callable(attr) and name not in cls.__dict__:
                    setattr(cls, name, innerPlugin(pluginName)(attr))
        return cls
    
    return wrapper


@contextmanager
def contextPlugin(pluginName):
    lastContext = _current_plugin.get()
    try:
        _current_plugin.set(pluginName)
        yield
    finally:
        _current_plugin.set(lastContext)


class MyWrapReadOnly(WrapReadOnly):
    def opendir(self, path, factory=None):
        return self._wrap_fs.opendir(path, factory)


class ZipFormatFile(OSFS):
    suffix_file = ""
    
    def opendir(self, path, factory=None):
        self.check()
        _path = pathlib.Path(self.validatepath(path).lstrip("\\").lstrip("/"))
        folder, parts = self._getRootPlugin(_path)
        _zipfs = MyWrapReadOnly(open_fs(f"zip://{self.root_path}/{folder}.{self.suffix_file}", False))
        if not len(parts):
            return _zipfs
        else:
            return _zipfs.opendir("/".join(parts))
    
    @staticmethod
    def _getRootPlugin(path: pathlib.Path):
        _parts = path.parts
        return _parts[0], _parts[1:]
    
    def getinfo(self, path, namespaces=None):
        lastInfo = super().getinfo(f"{path}.{self.suffix_file}", namespaces)
        lastInfo.raw["basic"]["is_dir"] = True
        lastInfo.raw["basic"]["name"] = lastInfo.raw["basic"]["name"].rstrip(f".{self.suffix_file}")
        if "details" in lastInfo.raw:
            lastInfo.raw["details"]["type"] = ResourceType.directory
        return lastInfo
    
    def listdir(self, path):
        self.check()
        _path = self.validatepath(path)
        sys_path = pathlib.Path(self._to_sys_path(_path).decode("utf-8"))
        return [file.stem for file in sys_path.iterdir() if file.suffix == f".{self.suffix_file}"]


class PluginFS(ZipFormatFile):
    suffix_file = "plugin"
    
    def __init__(self):
        super().__init__(str(global_cxt.pluginPath))


class PluginDataFS(OSFS):
    def __init__(self):
        super().__init__(str(global_cxt.pluginDataPath))


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


class BasePathOpener(Opener):
    filePattern = re.compile(r"^.*\..+$", re.I)
    
    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str) -> FS:
        
        fs = self.getImplFS(fs_url, parse_result, writeable, create, cwd)
        path = pathlib.Path(parse_result.resource)
        if (self.filePattern.fullmatch(str(path)) is None) and parse_result.resource:
            fs = fs.opendir(parse_result.resource)
        if self.filePattern.fullmatch(str(path)):
            print(path.parent)
        return fs
    
    @abstractmethod
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        pass


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
    
    def __init__(self):
        self.typeResource = ""
    
    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str) -> FS:
        path: str = parse_result.resource
        parts = fs_path.parts(path)
        if parts[1].lower() not in ["theme", "resource"]: raise errors.ResourceNotFound
        match parts[1].lower():
            case "theme":
                self.typeResource = "theme"
            case "resource":
                self.typeResource = "resource"
        parts.pop(1)
        path = fs_path.join(*parts)
        result = ParseResult(
            parse_result.protocol,
            parse_result.username,
            parse_result.password,
            path,
            parse_result.params,
            parse_result.path
        )
        return super().open_fs(fs_url, result, writeable, create, cwd)
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        if self.typeResource == "theme":
            return MyWrapReadOnly(ThemeFS())
        elif self.typeResource == "resource":
            return MyWrapReadOnly(ResourceFS())


import builtins


class OpenManager:
    def __init__(self, extra=False):
        self.original_open = builtins.open
        self.SCHEME_HINTS = {
            "s3": "Установите плагин: pip install fs-s3fs",
            "gs": "Установите плагин: pip install fs-gcsfs",
            "http": "Для HTTP/HTTPS требуется fs-http",
            "ftp": "Для FTP требуется fs-ftp",
        }
        self.extra = extra
    
    @lru_cache(maxsize=10)
    def _get_fs(self, folder):
        """Открывает FS с кешированием."""
        if not folder:
            return None
        try:
            return open_fs(folder)
        except errors.CreateFailed as e:
            scheme = folder.split("://")[0]
            hint = self.SCHEME_HINTS.get(scheme, "")
            raise ImportError(
                f"Не удалось открыть файловую систему {scheme}. {hint}\n{e}"
            ) from e
    
    @staticmethod
    def _check_writable(fs, mode):
        if any(c in mode for c in ('w', 'a', '+', 'x')):
            try:
                if not fs.getmeta().get("supports_write", True):
                    raise PermissionError("Файловая система доступна только для чтения")
            except errors.Unsupported:
                pass  # Если метаданные не поддерживаются
    
    def _custom_open(self, file, mode='r', **kwargs):
        if "://" in file:
            folder, filename = self._get_file(file)
            try:
                fs = self._get_fs(folder)
                self._check_writable(fs, mode)
                return fs.open(filename, mode=mode, **kwargs)
            except errors.ResourceError as e:
                raise FileNotFoundError(
                    f"Файл не найден: {file}. Проверьте путь и права доступа."
                ) from e
            except errors.Unsupported as e:
                raise ValueError(f"Неподдерживаемая операция: {e}") from e
        else:
            return self.original_open(file, mode=mode, **kwargs)
    
    def _extra_custom_open(self, file, mode="r", **kwargs):
        if "://" in file:
            protocol, path = self._get_file(file)
            
            return io.StringIO()
        else:
            return self.original_open(file, mode="r", **kwargs)
    
    @staticmethod
    def _get_file(file: str):
        protocol, path = file.split("://", 1)
        basedir, basename = fs_path.dirname(path), fs_path.basename(path)
        if protocol in ["plugin", "pldata"] and isActiveContextPlugin():
            basedir = f"{_current_plugin.get()}{basedir}"
        return f"{protocol}://{basedir}", basename
    
    def enable(self):
        builtins.open = self._custom_open
    
    def enable_extra(self):
        builtins.open = self._extra_custom_open
    
    def disable(self):
        builtins.open = self.original_open
    
    def __enter__(self):
        if self.extra:
            self.enable_extra()
        else:
            self.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()
