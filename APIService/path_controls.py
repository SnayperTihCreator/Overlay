import io
import sys
import zipfile
from functools import cache
from pathlib import Path
import os


@cache
def getAppPath():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(os.getcwd())
    )


class PluginPath:
    """Решает пути в стиле Godot: plugin:/, plugin_data:/, project:/."""
    
    def __init__(self, pluginName=None):
        self.pluginName = pluginName
    
    @classmethod
    def _resolvePluginPath(cls, pluginName, virtualPath):
        """Путь внутри ZIP-плагина (plugin:/plugin1/file.txt)."""
        if not pluginName:
            raise ValueError("Plugin name not set!")
        relPath = virtualPath.replace("plugin:/", "").lstrip("/")
        return f"plugins/{pluginName}.zip/{relPath}"
    
    @classmethod
    def _resolvePluginDataPath(cls, pluginName, virtualPath):
        """Путь к данным плагина (plugin_data:/file.txt → plugins/pldata/plugin1/file.txt)."""
        if not pluginName:
            raise ValueError("Plugin name not set!")
        relPath = virtualPath.replace("plugin_data:/", "").lstrip("/")
        return getAppPath() / "plugins" / "pldata" / pluginName / relPath
    
    @classmethod
    def _resolveProjectPath(cls, pluginName, virtualPath):
        """project:/file → папка с EXE/file."""
        rel_path = virtualPath.replace("project:/", "").lstrip("/")
        return getAppPath() / rel_path
    
    @cache
    def resolve(self, virtualPath):
        """Разрешает все типы путей (plugin:/, plugin_data:/, project:/)."""
        if virtualPath.startswith("plugin:/"):
            return self._resolvePluginPath(self.pluginName, virtualPath)
        elif virtualPath.startswith("plugin_data:/"):
            return self._resolvePluginDataPath(self.pluginName, virtualPath)
        elif virtualPath.startswith("project:/"):
            return self._resolveProjectPath(self.pluginName, virtualPath)
        return Path(virtualPath)
    
    def __truediv__(self, other):
        """Поддержка оператора / для удобства: path / "file.txt"."""
        return self.resolve(other)
    
    def __str__(self):
        return f"PluginPath(pluginName={self.pluginName})"
    
    # Чтобы PluginPath можно было передать в open()
    def open(self, virtualPath, mode="r"):
        """Аналог builtin open(), работающий с виртуальными путями."""
        return FileProject(self.pluginName).open(virtualPath, mode)
    
    def getRealPath(self, path=None):
        """Универсальный метод для классметода и экземпляра."""
        
        if path is None:  # Вызов как классметода
            cls = PluginPath
            path: str = self
            if not path.startswith("project:/"):
                raise ValueError("Classmethod supports only project:/ paths!")
            return cls._resolvePluginDataPath()
        
        # Вызов как метода экземпляра
        resolved = self.resolve(path)
        return str(resolved).replace(".zip/", ".zip!/") if isinstance(resolved, str) else resolved


class FileProject:
    """Унифицированная работа с файлами (ZIP/ФС)."""
    
    def __init__(self, pluginName=None):
        self.pathResolver = PluginPath(pluginName)
    
    def open(self, virtualPath, mode="r"):
        """Открывает файл как встроенный open()."""
        path: Path = self.pathResolver.resolve(virtualPath)
        
        # Режим записи/дозаписи (только для реальных файлов)
        if any(c in mode for c in ('w', 'a', 'x', '+')):
            if isinstance(path, str):
                raise PermissionError("Cannot write to files inside ZIP archives (plugin:/).")
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            return path.open(mode)
        
        # Чтение из ZIP
        if isinstance(path, str) and ".zip/" in path:
            zipPath, fileInZip = path.split(".zip/", 1)
            zipPath += ".zip"
            
            try:
                z = zipfile.ZipFile(zipPath, 'r')
                file = z.open(fileInZip)
                if 'b' not in mode:
                    return io.TextIOWrapper(file, encoding='utf-8')
                return file
            except KeyError:
                raise FileNotFoundError(f"File {fileInZip} not found in {zipPath}")
        
        # Чтение обычного файла
        return path.open(mode)
    
    def read(self, virtualPath, mode="r"):
        """Читает файл по виртуальному пути."""
        with self.pathResolver.open(virtualPath, mode) as f:
            return f.read()
    
    def write(self, virtualPath, data, mode="w"):
        """Записывает данные в файл (только в plugin_data:/ или project:/)."""
        with self.pathResolver.open(virtualPath, mode) as f:
            f.write(data)
    
    def append(self, virtualPath, data, mode="a"):
        """Дописывает данные в файл (только в plugin_data:/ или project:/)."""
        self.write(virtualPath, data, mode)
    
    def getRealPath(self, virtualPath):
        """Возвращает реальный путь (включая путь до ZIP, если файл внутри архива)."""
        path = self.pathResolver.resolve(virtualPath)
        if isinstance(path, str):
            return str(Path(path.replace(".zip/", ".zip!/")))  # Путь в стиле ZIP: file.zip!/inner.txt
        return path


__all__ = ["getAppPath", "FileProject", "PluginPath"]
