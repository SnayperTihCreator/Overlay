import pathlib
from abc import abstractmethod
import re

from fs.base import FS
from fs.opener import Opener
from fs.opener.parse import ParseResult
from fs import open_fs
from fs.enums import ResourceType
from fs.osfs import OSFS
from fs.wrap import WrapReadOnly


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
    
    def open(self, path, mode="r", buffering=-1, encoding=None,
             errors=None, newline="", line_buffering=False, **options
             ):
        folder, file = path.rsplit("/", 1)
        if folder and file:
            zipfs = self.opendir(folder)
            return zipfs.open(file, mode, buffering, encoding, errors, newline, line_buffering, **options)
        return super().open(path, mode, buffering, encoding, errors, newline, line_buffering, **options)
    
    @staticmethod
    def _getRootPlugin(path: pathlib.Path):
        _parts = path.parts
        return _parts[0], _parts[1:]
    
    def getinfo(self, path, namespaces=None):
        folder, file = path.rsplit("/", 1)
        if folder and file:
            lastInfo = self.opendir(folder).getinfo(file, namespaces)
        else:
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
