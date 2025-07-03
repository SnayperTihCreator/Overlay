from typing import Union, Optional
import io

from PySide6.QtCore import QFile, QIODevice, QTextStream
from fs.base import FS
from fs.info import Info
from fs.opener import Opener, registry
from fs.opener.parse import ParseResult
from fs.subfs import ClosingSubFS
from fs import errors, open_fs

import pathlib


class SubFileControlsFS(ClosingSubFS):
    def __init__(self, parent: "FileControlFS", path: str):
        super().__init__(parent, path)
        self._protocol = parent._protocol


class FileControlFS(FS):
    subfs_class = SubFileControlsFS
    
    def __init__(self, protocol):
        super().__init__()
        self._protocol = protocol
        self._base_path = global_cxt.appPath
        match protocol:
            case "plugin":
                self._base_path = global_cxt.pluginPath
            case "pldata":
                self._base_path = global_cxt.pluginDataPath
            case "qt":
                self._base_path = pathlib.Path("qrc:/")
    
    def getinfo(self, path, namespaces=None):
        print(self._protocol, path)
        if self._protocol == "pldata":
            basic = dict(name=path, is_dir=(self._base_path / path.lstrip("/")).is_dir())
        elif self._protocol == "plugin":
            basic = dict(name="none", is_dir=True)
        else:
            basic = dict(name="none", is_dir=False)
        
        raw_info = dict(basic=basic)
        return Info(raw_info)
    
    def listdir(self, path):
        print(path)
        if self._protocol == "plugin":
            return [path.name for path in (self._base_path / path.lstrip("/")).iterdir() if path.suffix == ".zip"]
        if self._protocol == "pldata":
            return [path.name for path in (self._base_path / path.lstrip("/")).iterdir()]
    
    def makedir(self, path, permissions=None, recreate=False):
        if self._protocol in ["plugin", "qt"]:
            raise errors.CreateFailed("Не возможно создать папку")
        newPath = self._base_path / path.lstrip("/")
        newPath.mkdir(parents=True, exist_ok=True)
        return ClosingSubFS(self, path)
    
    def openbin(self, path, mode="r", buffering=-1, **options):
        pass
    
    def remove(self, path):
        pass
    
    def removedir(self, path):
        pass
    
    def setinfo(self, path, info):
        pass
    
    def getsyspath(self, path):
        return str(self._base_path / path.lstrip("/"))
    
    def opendir(self, path: str, factory=None):
        print(self._protocol, path, factory)
        path = self.validatepath(path)
        if self._protocol != "plugin":
            return super().opendir(path, factory)
        if self._protocol != "qt":
            pass
        if path.count("/") > 1:
            _, plugin, path = path.split("/", 2)
            path = f"!/{path}"
        else:
            plugin, path = path, ""
        return open_fs(f"zip://{self.getsyspath('')}/{plugin}.zip{path}")


@registry.install
class PluginPathOpener(Opener):
    protocols = ["plugin", "pldata", "project"]
    
    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str) -> FS:
        return FileControlFS(parse_result.protocol)


class FileStorage:
    """Обертка над QFile с интерфейсом, аналогичным Python FileIO"""
    
    def __init__(self, filename: str, mode: str = 'r', encoding: str = 'utf-8'):
        """
        Args:
            filename: Путь к файлу
            mode: Режим открытия ('r', 'w', 'a', 'b', 't' и их комбинации)
            encoding: Кодировка для текстового режима
        """
        self._file = QFile(filename)
        self._mode = mode
        self._encoding = encoding
        self._text_stream: Optional[QTextStream] = None
        self._buffer = io.StringIO() if 't' in mode else io.BytesIO()
        
        qt_mode = self._parse_mode(mode)
        if not self._file.open(qt_mode):
            raise IOError(f"Could not open file {filename} in mode {mode}")
        
        # Для режима чтения загружаем данные сразу в буфер
        if 'r' in mode:
            data = self._file.readAll().data()
            if 't' in mode:
                self._buffer.write(bytes(data).decode(encoding))
            else:
                self._buffer.write(bytes(data))
            self._buffer.seek(0)
    
    def _parse_mode(self, mode: str) -> QIODevice.OpenModeFlag:
        """Преобразует Python-режим в QIODevice флаги"""
        qt_mode = QIODevice.OpenModeFlag.NotOpen
        
        if 'r' in mode:
            qt_mode |= QIODevice.OpenModeFlag.ReadOnly
        if 'w' in mode:
            qt_mode |= QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Truncate
        if 'a' in mode:
            qt_mode |= QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Append
        if '+' in mode:
            qt_mode |= QIODevice.OpenModeFlag.ReadWrite
        
        if 't' not in mode and 'b' not in mode:
            qt_mode |= QIODevice.OpenModeFlag.Text
        elif 't' in mode:
            qt_mode |= QIODevice.OpenModeFlag.Text
        
        return qt_mode
    
    def read(self, size: int = -1) -> Union[str, bytes]:
        """Читает данные из файла"""
        if 'r' not in self._mode and '+' not in self._mode:
            raise IOError("File not open for reading")
        
        if 't' in self._mode:
            return self._buffer.read(size)
        else:
            data = self._buffer.read(size)
            return bytes(data) if isinstance(data, (bytearray, memoryview)) else data
    
    def readline(self, size: int = -1) -> Union[str, bytes]:
        """Читает строку из файла"""
        if 'r' not in self._mode and '+' not in self._mode:
            raise IOError("File not open for reading")
        
        return self._buffer.readline(size)
    
    def write(self, data: Union[str, bytes, bytearray]) -> int:
        """Записывает данные в файл"""
        if 'w' not in self._mode and 'a' not in self._mode and '+' not in self._mode:
            raise IOError("File not open for writing")
        
        if 't' in self._mode and isinstance(data, (bytes, bytearray)):
            data = data.decode(self._encoding)
        elif 'b' in self._mode and isinstance(data, str):
            data = data.encode(self._encoding)
        
        return self._buffer.write(data)
    
    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        """Устанавливает позицию в файле"""
        return self._buffer.seek(offset, whence)
    
    def tell(self) -> int:
        """Возвращает текущую позицию в файле"""
        return self._buffer.tell()
    
    def flush(self) -> None:
        """Сбрасывает буферы на диск"""
        if self._file.isOpen() and ('w' in self._mode or 'a' in self._mode or '+' in self._mode):
            self._file.seek(0)
            data = self._buffer.getvalue()
            if 't' in self._mode:
                self._file.write(data.encode(self._encoding))
            else:
                self._file.write(bytes(data))
            self._file.flush()
    
    def close(self) -> None:
        """Закрывает файл"""
        if self._file.isOpen():
            self.flush()
            self._file.close()
    
    def __enter__(self):
        """Поддержка менеджера контекста"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка менеджера контекста"""
        self.close()
    
    def __iter__(self):
        """Поддержка итерации по строкам"""
        return self
    
    def __next__(self) -> Union[str, bytes]:
        """Итерация по строкам"""
        line = self.readline()
        if not line:
            raise StopIteration
        return line
    
    # Свойства аналогичные FileIO
    @property
    def mode(self) -> str:
        """Возвращает режим открытия файла"""
        return self._mode
    
    @property
    def name(self) -> str:
        """Возвращает имя файла"""
        return self._file.fileName()
    
    @property
    def encoding(self) -> str:
        """Возвращает кодировку файла"""
        return self._encoding
    
    @property
    def closed(self) -> bool:
        """Проверяет, закрыт ли файл"""
        return not self._file.isOpen()
