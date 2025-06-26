from PySide6.QtCore import QFile, QIODevice
from typing import Union, Optional


class _QtResourceBinaryWrapper:
    """Внутренний класс-обертка для бинарного режима"""
    
    def __init__(self, resource_path: str, mode: QIODevice.OpenModeFlag.ReadOnly):
        self._file = QFile(resource_path)
        if not self._file.open(mode):
            raise RuntimeError(f"Failed to open resource: {resource_path}")
        self._pos = 0
    
    def read(self, size: int = -1) -> bytes:
        data = self._file.read(size) if size != -1 else self._file.readAll()
        self._pos += data.size()
        return data.data()
    
    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:  # SEEK_SET
            self._file.seek(offset)
        elif whence == 1:  # SEEK_CUR
            self._file.seek(self._file.pos() + offset)
        elif whence == 2:  # SEEK_END
            self._file.seek(self._file.size() + offset)
        self._pos = self._file.pos()
        return self._pos
    
    def tell(self) -> int:
        return self._file.pos()
    
    def close(self) -> None:
        self._file.close()
    
    def __enter__(self) -> '_QtResourceBinaryWrapper':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
    
    def __iter__(self):
        while not self._file.atEnd():
            yield self.read(4096)


class _QtResourceTextWrapper(_QtResourceBinaryWrapper):
    """Внутренний класс-обертка для текстового режима"""
    
    def __init__(self, resource_path: str, mode: QIODevice.OpenModeFlag.ReadOnly,
                 encoding: Optional[str] = 'utf-8',
                 errors: Optional[str] = None,
                 newline: Optional[str] = None):
        super().__init__(resource_path, mode)
        self._encoding = encoding or 'utf-8'
        self._errors = errors or 'strict'
        self._newline = newline
        self._buffer = ''
    
    def read(self, size: int = -1) -> str:
        binary_data = super().read(size)
        text = binary_data.decode(self._encoding, errors=self._errors)
        
        if self._newline is not None and self._newline != '':
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            if self._newline != '\n':
                text = text.replace('\n', self._newline)
        
        return text
    
    def readline(self, limit: int = -1) -> str:
        line = []
        while True:
            c = self.read(1)
            if not c or c == '\n':
                break
            line.append(c)
            if 0 < limit <= len(line):
                break
        return ''.join(line)
    
    def __iter__(self):
        while not self._file.atEnd():
            yield self.readline()


class QtResourceDescriptor:
    """
    Класс для работы с ресурсами PySide6 с поддержкой различных режимов открытия и кодировок.

    Примеры использования:
        # Чтение текста с кодировкой по умолчанию (utf-8)
        with QtResourceDescriptor.open(":/files/example.txt", 'r') as f:
            content = f.read()

        # Чтение бинарных данных
        with QtResourceDescriptor.open(":/images/photo.png", 'rb') as f:
            data = f.read()

        # Чтение текста с указанной кодировкой
        with QtResourceDescriptor.open(":/files/example.txt", 'r', encoding='cp1251') as f:
            content = f.read()
    """
    
    @staticmethod
    def open(resource_path: str, mode: str = 'r', encoding: Optional[str] = None, errors: Optional[str] = None,
             newline: Optional[str] = None) -> Union[_QtResourceTextWrapper, _QtResourceBinaryWrapper]:
        """
        Открывает ресурс в указанном режиме аналогично стандартному open().

        Args:
            resource_path: Путь к ресурсу в системе Qt (начинается с :/)
            mode: Режим открытия файла (аналогичен режимам open())
            encoding: Кодировка для текстовых режимов
            errors: Обработка ошибок кодирования
            newline: Контроль перевода строк

        Returns:
            Файловый объект (текстовый или бинарный)

        Raises:
            ValueError: При некорректном режиме или параметрах
            RuntimeError: При ошибке открытия ресурса
        """
        # Режимы только для чтения, так как ресурсы обычно read-only
        if any(c in mode for c in ('w', 'a', '+')):
            raise ValueError("Qt resources are read-only. Use 'r' or 'rb' modes only.")
        
        qt_mode = QIODevice.OpenModeFlag.ReadOnly
        if 'b' in mode:
            # Бинарный режим
            return _QtResourceBinaryWrapper(resource_path, qt_mode)
        else:
            # Текстовый режим
            return _QtResourceTextWrapper(resource_path, qt_mode, encoding, errors, newline)
