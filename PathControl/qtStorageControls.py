import datetime
import io
from typing import Optional, Union

from PySide6.QtCore import QFileInfo, QDir, QFile, QIODevice, QBuffer, QDataStream, QByteArray, QTextStream
from fs import ResourceType, errors
from fs.base import FS
from fs.info import Info
from fs.mode import Mode
from fs.opener import registry

from PathControl.storageControls import BasePathOpener


class BinaryFileDescriptor:
    def __init__(self, filename, mode='rb', buffering=-1, **options):
        """
        Инициализация бинарного дескриптора файла

        :param filename: имя файла
        :param mode: режим открытия ('r', 'w', 'a', 'b', '+')
        :param buffering: размер буфера (-1 - системный, 0 - без буфера, >0 - размер буфера)
        :param options: дополнительные параметры (encoding, errors, newline - игнорируются для бинарного режима)
        """
        self.filename = filename
        self.mode = mode
        self.buffering = buffering
        self.options = options
        self.file = QFile(filename)
        self.stream = None
        self.buffer = None
        
        # Парсим режим открытия
        open_mode = QIODevice.OpenModeFlag.NotOpen
        if 'r' in mode:
            open_mode = QIODevice.OpenModeFlag.ReadOnly
        elif 'w' in mode:
            open_mode = QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Truncate
        elif 'a' in mode:
            open_mode = QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Append
        
        if '+' in mode:
            open_mode = (open_mode & ~(
                    QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.WriteOnly)) | QIODevice.OpenModeFlag.ReadWrite
        
        # Всегда добавляем Unbuffered, если явно не указана буферизация
        if buffering == 0:
            open_mode |= QIODevice.OpenModeFlag.Unbuffered
        
        # Дополнительные флаги из options
        if options.get('exclusive', False):
            open_mode |= QIODevice.OpenModeFlag.NewOnly
        if options.get('truncate', 'w' in mode):
            open_mode |= QIODevice.OpenModeFlag.Truncate
        
        if not self.file.open(open_mode):
            raise IOError(f"Не удалось открыть файл {filename} в режиме {mode}")
        
        # Настройка буферизации
        if buffering > 0:
            self.buffer = QBuffer()
            self.buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            self.stream = QDataStream(self.buffer)
        else:
            self.stream = QDataStream(self.file)
        
        self.stream.setVersion(QDataStream.Version.Qt_6_0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def write(self, data):
        """Запись бинарных данных в файл"""
        
        if self.buffer is not None:
            self.stream << data if isinstance(data, QByteArray) else self.stream.writeRawData(data)
            if self.buffer.size() >= self.buffering:
                self.flush()
        else:
            self.stream << data if isinstance(data, QByteArray) else self.stream.writeRawData(data)
    
    def read(self, size=-1):
        """
        Чтение бинарных данных из файла

        :param size: количество байт для чтения (-1 - читать до конца файла)
        :return: QByteArray с прочитанными данными
        """
        if self.buffer is not None:
            if size == -1:
                # Читаем все из файла в буфер, затем возвращаем
                data = self.file.readAll()
                self.buffer.buffer().append(data)
                return data
            else:
                # Если в буфере недостаточно данных, читаем из файла
                if self.buffer.bytesAvailable() < size:
                    needed = size - self.buffer.bytesAvailable()
                    data = self.file.read(needed)
                    self.buffer.buffer().append(data)
                return self.buffer.read(size)
        else:
            if size == -1:
                return self.file.readAll()
            return self.file.read(size)
    
    def close(self):
        """Закрытие файла с предварительным сбросом буфера"""
        if self.file.isOpen():
            self.flush()
            if self.buffer is not None:
                self.buffer.close()
            self.file.close()
    
    def seek(self, pos, whence=0):
        """Перемещение указателя в файле"""
        if whence == 0:  # SEEK_SET
            pass
        elif whence == 1:  # SEEK_CUR
            pos += self.tell()
        elif whence == 2:  # SEEK_END
            pos += self.file.size()
        
        if self.buffer is not None:
            self.flush()  # Сбрасываем буфер перед seek
        self.file.seek(pos)
    
    def tell(self):
        """Получение текущей позиции в файле"""
        if self.buffer is not None:
            # Позиция в файле + позиция в буфере записи
            return self.file.pos() - self.buffer.bytesAvailable()
        return self.file.pos()
    
    def flush(self):
        """Сброс буферов на диск"""
        if self.buffer is not None and self.buffer.size() > 0:
            # Записываем данные из буфера в файл
            self.file.write(self.buffer.data())
            self.buffer.buffer().clear()
        self.file.flush()
    
    def truncate(self, size=None):
        """Обрезание файла до указанного размера"""
        if size is None:
            size = self.tell()
        self.file.resize(size)


class QrcFS(FS):
    
    def getinfo(self, path, namespaces=None):
        _info = QFileInfo(f":/{path.lstrip('/')}")
        raw_info = {}
        basic = dict(name=_info.fileName(), is_dir=_info.isDir())
        raw_info["basic"] = basic
        
        
        
        if namespaces and ("details" in namespaces):
            details = dict(
                size=_info.size(),
                type=ResourceType.file if _info.isFile() else ResourceType.directory,
                modified=datetime.datetime.now()
            )
            raw_info["details"] = details
        return Info(raw_info)
    
    def listdir(self, path):
        return QDir(f":/{path.lstrip('/')}").entryList()
    
    def makedir(self, path, permissions=None, recreate=False):
        raise errors.ResourceReadOnly("Не возможно создать папку")
    
    def openbin(self, path, mode="r", buffering=-1, **options):
        _mode = Mode(mode)
        _mode.validate(set("rtb"))
        return BinaryFileDescriptor(f":/{path.lstrip('/')}", _mode.to_platform_bin(), buffering, **options)
    
    def remove(self, path):
        raise errors.ResourceReadOnly("Нельзя удалить")
    
    def removedir(self, path):
        raise errors.ResourceReadOnly("Нельзя удалить")
    
    def setinfo(self, path, info):
        raise errors.ResourceReadOnly("Не возможно изменить")


@registry.install
class QrcPathOpener(BasePathOpener):
    protocols = ["qrc", "qt"]
    
    def getImplFS(self, url, parse_result, writable, create, cwd) -> FS:
        return QrcFS()


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
