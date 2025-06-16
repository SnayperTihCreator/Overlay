import toml
from pathlib import Path
from typing import Any
from dataclasses import dataclass

from box import Box


@dataclass
class Defaults:
    draggable_window = {"window": {"width": 300, "height": 200}}
    overlay_widget = {}
    apps = {
        "websockets": {
            "IN": [8000, 8010],
            "OUT": [8015, 8020]
        }
    }


class Config:
    def __init__(self, path, plugin_type, config_name="config", create_is_not=True):
        self._config_name = config_name
        self._create_is_not = create_is_not
        self._default_config = getattr(Defaults, plugin_type)
        self._load_path = None
        self._config: Box = self._load_config(path)
    
    def _load_config(self, path) -> Box[str, Any]:
        self._load_path = path
        config_path = Path(path).parent / f"{self._config_name}.toml"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return Box(toml.load(f))
        except (FileNotFoundError, toml.TomlDecodeError):
            # Если файла нет или он поврежден, создаем новый с дефолтными значениями
            if self._create_is_not:
                with open(config_path, "w", encoding="utf-8") as f:
                    toml.dump(self._default_config, f)
            return Box(self._default_config)
    
    def __getattr__(self, item):
        return getattr(self._config, item)
    
    def reload(self):
        self._config = self._load_config(self._load_path)
    
    def plugin_path(self):
        return Path(self._load_path).parent
