import builtins
import io
import pathlib
from functools import lru_cache

from fs import errors, open_fs, path as fs_path

from core.context import _current_plugin, isActiveContextPlugin


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
    def _get_fs(self, folder, mode):
        """Открывает FS с кешированием."""
        scheme, sub_folder = folder.split("://", 1)
        if not folder:
            return None
        try:
            return open_fs(folder)
        except errors.ResourceNotFound as e:
            if not (("w" in mode) or ("x" in mode)): raise e
            fs = open_fs(f"{scheme}://")
            return fs.makedir(sub_folder)
        except errors.CreateFailed as e:
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
        if not isinstance(file, pathlib.Path) and "://" in file:
            folder, filename = self._get_file(file)
            try:
                fs = self._get_fs(folder, mode)
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
