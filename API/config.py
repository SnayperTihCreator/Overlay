import toml
from pathlib import Path
from typing import Any
from dataclasses import dataclass

from box import Box
from APIService.path_controls import PluginPath


@dataclass
class Defaults:
    draggable_window = {
        "window": {"width": 300, "height": 200}
    }
    overlay_widget = {}
    apps = {
        "websockets": {"IN": [8000, 8010], "OUT": [8015, 8020]},
        "shortkey": {"open": "shift+alt+o"}
    }


class Config:
    def __init__(self, path, plugin_type, config_name="config", create_is_not=True):
        self._config_name = config_name
        self._create_is_not = create_is_not
        self._default_config = getattr(Defaults, plugin_type)
        self._plugin_type = plugin_type
        plugin_name = Path(path).parent.name if ".zip" else Path(path).name
        self._load_path = PluginPath(plugin_name)
        self._config: Box = self._load_config()
    
    def _load_config(self) -> Box[str, Any]:
        try:
            with self.loadFile(f"{self._config_name}.toml", "r") as f:
                return Box(toml.load(f))
        except (FileNotFoundError, toml.TomlDecodeError) as e:
            print(f"{type(e)}: {e}")
            # Если файла нет или он поврежден, создаем новый с дефолтными значениями
            if self._create_is_not:
                with self.loadFile(f"{self._config_name}.toml", "w") as f:
                    toml.dump(self._default_config, f)
            return Box(self._default_config)
    
    def loadFile(self, path, mode="r", data_storage="auto"):
        prefix = data_storage
        if data_storage == "auto" and "w" not in mode:
            prefix = "plugin" if self._plugin_type != "apps" else "project"
        elif data_storage == "auto" and "w" in mode:
            prefix = "plugin_data" if self._plugin_type != "apps" else "project"
        return self._load_path.open(f"{prefix}:/{path}", mode)
    
    def __getattr__(self, item):
        return getattr(self._config, item)
    
    def reload(self):
        self._config = self._load_config()
    
    def plugin_path(self):
        return self._load_path
