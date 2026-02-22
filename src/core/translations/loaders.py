import logging
import io
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, QTextStream, QDirIterator, QFileInfo

from ldt.io_drives.drivers import BaseDriver

# Setup standard logger
logger = logging.getLogger(__name__)


class BaseLoader:
    def is_valid(self) -> bool: return True
    
    def get_available_langs(self) -> set[str]: return set()
    
    def load(self, lang: str) -> dict: return {}


class QRCLoader(BaseLoader):
    """
    Loader from Qt Resources (:/i18n/).
    """
    
    def __init__(self, base_path: str, driver: BaseDriver, extension: str = "yaml"):
        self.base_path = base_path if base_path.endswith('/') else base_path + '/'
        self.driver = driver
        self.ext = extension.strip('.')
        
        self._valid = QFileInfo(self.base_path).exists()
        if not self._valid:
            logger.warning(f"QRC path not found: {self.base_path}")
    
    def is_valid(self) -> bool:
        return self._valid
    
    def get_available_langs(self) -> set[str]:
        if not self._valid: return set()
        
        langs = set()
        # Iterate over QRC directory
        it = QDirIterator(self.base_path, QDirIterator.NoIteratorFlags)
        while it.hasNext():
            it.next()  # Advance iterator
            info = it.fileInfo()
            if info.suffix() == self.ext:
                langs.add(info.baseName())
        return langs
    
    def load(self, lang: str) -> dict:
        if not self._valid: return {}
        path = f"{self.base_path}{lang}.{self.ext}"
        
        qfile = QFile(path)
        data = {}
        
        if qfile.open(QIODevice.ReadOnly | QIODevice.Text):
            try:
                # Read QRC file to string stream
                stream = io.StringIO(QTextStream(qfile).readAll())
                data = self.driver.read_stream(stream)
            except Exception as e:
                # Log parsing errors with traceback
                logger.error(f"Failed to parse QRC file '{path}': {e}", exc_info=True)
            finally:
                qfile.close()
        else:
            # File exists in list but cannot be opened (rare)
            logger.warning(f"Could not open QRC file: {path}")
        
        return data


class FileLoader(BaseLoader):
    """
    Loader from external directory using Pathlib.
    """
    
    def __init__(self, directory: str | Path, driver: BaseDriver, extension: str = "yaml"):
        self.directory = Path(directory).resolve()
        self.driver = driver
        self.ext = f".{extension.lstrip('.')}"
        
        if not self.directory.exists():
            logger.warning(f"Directory not found: {self.directory}")
    
    def is_valid(self) -> bool:
        return self.directory.exists() and self.directory.is_dir()
    
    def get_available_langs(self) -> set[str]:
        if not self.is_valid():
            return set()
        
        try:
            return {f.stem for f in self.directory.glob(f"*{self.ext}") if f.is_file()}
        except Exception as e:
            logger.error(f"Error reading directory '{self.directory}': {e}", exc_info=True)
            return set()
    
    def load(self, lang: str) -> dict:
        if not self.is_valid():
            return {}
        
        file_path = self.directory / f"{lang}{self.ext}"
        
        if not file_path.exists():
            # Not critical, maybe language just doesn't exist in this folder
            logger.warning(f"Localization file not found: {file_path}")
            return {}
        
        try:
            data = self.driver.read(file_path)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            # File exists but is broken
            logger.error(f"Failed to load file '{file_path}': {e}", exc_info=True)
            return {}
