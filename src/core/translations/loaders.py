import logging
import io
from pathlib import Path
from typing import Dict, Set

from PySide6.QtCore import QFile, QIODevice, QTextStream, QDirIterator, QFileInfo
from ldt.io_drives.drivers import BaseDriver

from core.logger import handler

logger = logging.getLogger("I18n.Loaders")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class BaseLoader:
    def is_valid(self) -> bool: return True
    
    def get_available_langs(self) -> Set[str]: return set()
    
    def load(self, lang: str) -> Dict: return {}


class QRCLoader(BaseLoader):
    """Загрузчик из ресурсов Qt (:/i18n/) с привязкой к драйверу Nexus"""
    
    def __init__(self, base_path: str, driver: BaseDriver, extension: str = "yaml"):
        self.base_path = base_path if base_path.endswith('/') else base_path + '/'
        self.driver = driver
        self.ext = extension.strip('.')
        
        self._valid = QFileInfo(self.base_path).exists()
        if not self._valid:
            logger.warning(f"QRC путь не найден: {self.base_path}")
    
    def is_valid(self) -> bool:
        return self._valid
    
    def get_available_langs(self) -> Set[str]:
        if not self._valid: return set()
        langs = set()
        it = QDirIterator(self.base_path, QDirIterator.NoIteratorFlags)
        while it.hasNext():
            info = QFileInfo(it.next())
            if info.suffix() == self.ext:
                langs.add(info.baseName())
        return langs
    
    def load(self, lang: str) -> Dict:
        if not self._valid: return {}
        path = f"{self.base_path}{lang}.{self.ext}"
        
        qfile = QFile(path)
        data = {}
        if qfile.open(QIODevice.ReadOnly | QIODevice.Text):
            try:
                stream = io.StringIO(QTextStream(qfile).readAll())
                data = self.driver.read_stream(stream)
            except Exception as e:
                logger.error(f"Ошибка парсинга QRC {path}: {e}")
            finally:
                qfile.close()
        return data


class FileLoader(BaseLoader):
    """Загрузчик из внешней директории с использованием Pathlib"""
    
    def __init__(self, directory: str | Path, driver: BaseDriver, extension: str = "yaml"):
        self.directory = Path(directory).resolve()
        self.driver = driver
        self.ext = f".{extension.lstrip('.')}"
        
        if not self.directory.exists():
            logger.warning(f"Директория не найдена: {self.directory}")
    
    def is_valid(self) -> bool:
        return self.directory.exists() and self.directory.is_dir()
    
    def get_available_langs(self) -> Set[str]:
        if not self.is_valid():
            return set()
        
        try:
            return {f.stem for f in self.directory.glob(f"*{self.ext}") if f.is_file()}
        except Exception as e:
            logger.error(f"Ошибка чтения {self.directory}: {e}")
            return set()
    
    def load(self, lang: str) -> Dict:
        if not self.is_valid():
            return {}
        
        file_path = self.directory / f"{lang}{self.ext}"
        
        if not file_path.exists():
            logger.warning(f"Файл локализации не найден: {file_path}")
            return {}
        
        try:
            data = self.driver.read(file_path)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Ошибка загрузки файла {file_path}: {e}")
            return {}
