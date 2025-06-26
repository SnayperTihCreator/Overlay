from pathlib import Path
import zipfile
import sys
import io


class PluginPath:
    """Решает пути в стиле Godot: plugin:/, plugin_data:/, project:/."""
    
    def __init__(self, pluginName=None):
        self.pluginName = pluginName
        self.appPath = self.getAppPath()
    
    @staticmethod
    def getAppPath():
        """Статический метод для получения пути к папке проекта."""
        return Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent
    
    def _resolvePluginPath(self, virtualPath):
        """Путь внутри ZIP-плагина (plugin:/plugin1/file.txt)."""
        if not self.pluginName:
            raise ValueError("Plugin name not set!")
        relPath = virtualPath.replace("plugin:/", "").lstrip("/")
        return f"plugins/{self.pluginName}.zip/{relPath}"
    
    def _resolvePluginDataPath(self, virtualPath):
        """Путь к данным плагина (plugin_data:/file.txt → plugins/pldata/plugin1/file.txt)."""
        if not self.pluginName:
            raise ValueError("Plugin name not set!")
        relPath = virtualPath.replace("plugin_data:/", "").lstrip("/")
        return self.appPath / "plugins" / "pldata" / self.pluginName / relPath
    
    def resolve(self, virtualPath):
        """Разрешает все типы путей (plugin:/, plugin_data:/, project:/)."""
        if virtualPath.startswith("plugin:/"):
            return self._resolvePluginPath(virtualPath)
        elif virtualPath.startswith("plugin_data:/"):
            return self._resolvePluginDataPath(virtualPath)
        elif virtualPath.startswith("project:/"):
            return self._resolveProjectPath(virtualPath)
        return Path(virtualPath)
    
    def _resolveProjectPath(self, virtualPath):
        """project:/file → папка с EXE/file."""
        rel_path = virtualPath.replace("project:/", "").lstrip("/")
        return self.getAppPath() / rel_path
    
    def __truediv__(self, other):
        """Поддержка оператора / для удобства: path / "file.txt"."""
        return self.resolve(other)
    
    def __str__(self):
        return f"PluginPath(pluginName={self.pluginName})"
    
    # Чтобы PluginPath можно было передать в open()
    def open(self, virtualPath, mode="r"):
        """Аналог builtin open(), работающий с виртуальными путями."""
        return FileIO(self.pluginName).open(virtualPath, mode)
    
    def getRealPath(self, path=None):
        """Универсальный метод для классметода и экземпляра."""
        
        if path is None:  # Вызов как классметода
            cls = PluginPath
            path = self
            if not path.startswith("project:/"):
                raise ValueError("Classmethod supports only project:/ paths!")
            rel_path = path.replace("project:/", "").lstrip("/")
            return cls.getAppPath() / rel_path
        
        # Вызов как метода экземпляра
        resolved = self.resolve(path)
        return str(resolved).replace(".zip/", ".zip!/") if isinstance(resolved, str) else resolved
    
# Как классметод (только project:/)
print(PluginPath.getRealPath("project:/config.json"))  # Корректно
# PluginPath.getRealPath("plugin:/file.txt")    # Ошибка!

# Как метод экземпляра (все пути)
path = PluginPath("my_plugin")
path.getRealPath("plugin:/file.txt")      # Работает
path.getRealPath("project:/config.json")  # Тоже работает