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


class PluginFS(OSFS):
    def __init__(self):
        super().__init__(str(global_cxt.pluginPath))
    
    def opendir(self, path, factory=None):
        self.check()
        _path = pathlib.Path(self.validatepath(path).lstrip("\\").lstrip("/"))
        folder, parts = self._getRootPlugin(_path)
        _zipfs = MyWrapReadOnly(open_fs(f"zip://{self.root_path}/{folder}.plugin", False))
        if not len(parts):
            return _zipfs
        else:
            return _zipfs.opendir("/".join(parts))
    
    def _to_sys_path(self, path):
        if not isActiveContextPlugin():
            return super()._to_sys_path(path)
        sys_path = fsencode(
            os.path.join(self._root_path, _current_plugin.get() + ".plugin!", path.lstrip("/").replace("/", os.sep))
        )
        print(sys_path)
        return sys_path
    
    @staticmethod
    def _getRootPlugin(path: pathlib.Path):
        if isActiveContextPlugin():
            return _current_plugin.get(), path.parts[:]
        _parts = path.parts
        return _parts[0], _parts[1:]
    
    def getinfo(self, path, namespaces=None):
        lastInfo = super().getinfo(f"{path}.zip", namespaces)
        lastInfo.raw["basic"]["is_dir"] = True
        lastInfo.raw["basic"]["name"] = lastInfo.raw["basic"]["name"].rstrip(".plugin")
        if "details" in lastInfo.raw:
            lastInfo.raw["details"]["type"] = ResourceType.directory
        return lastInfo
    
    def listdir(self, path):
        self.check()
        _path = self.validatepath(path)
        sys_path = pathlib.Path(self._to_sys_path(_path).decode("utf-8"))
        return [file.stem for file in sys_path.iterdir() if file.suffix == ".plugin"]


class PluginDataFS(OSFS):
    def __init__(self):
        super().__init__(str(global_cxt.pluginDataPath))
    
    def _to_sys_path(self, path):
        if not isActiveContextPlugin():
            return super()._to_sys_path(path)
        sys_path = fsencode(
            os.path.join(self._root_path, _current_plugin.get(), path.lstrip("/").replace("/", os.sep))
        )
        return sys_path


class ProjectFS(OSFS):
    def __init__(self):
        super().__init__(str(global_cxt.appPath))


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
    
    @lru_cache(maxsize=128)
    def _split_url(self, path):
        """Разбивает путь на (папку, имя файла) с помощью fs.opener.parse."""
        if "://" not in path:
            return None, path  # Локальный путь
        
        try:
            # Парсим URL стандартным для fs методом
            parse_result = parse_fs_url(path)
            scheme = parse_result.protocol
            
            # Формируем папку и имя файла
            folder_path = parse_result.resource
            if not folder_path:
                return f"{scheme}://", ""
            
            path_parts = folder_path.split("/")
            if len(path_parts) == 1:
                return f"{scheme}://{path_parts[0]}", ""
            
            folder = f"{scheme}://{'/'.join(path_parts[:-1])}"
            filename = path_parts[-1]
            return (folder.rstrip("/"), filename) if filename else (folder, "")
        
        except Exception as e:
            raise ValueError(f"Ошибка парсинга пути: {path}") from e
    
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
