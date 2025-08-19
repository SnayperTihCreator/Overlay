from typing import Optional, Literal
import io
from typing import Any
from dataclasses import dataclass

from box import Box
import toml


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
    setting = {}
    theme = {
        "plugin": {
            "name": "<unknown>"
        },
        "colors": {
            "base": "#6e738d",
            "main_text": "#cad3f5",
            "alt_text": "#8aadf4"
        }
    }


class Config:
    def __init__(self, plugin_name, plugin_type: Literal["draggable_window", "overlay_widget", "apps", "setting", "theme"], config_name="config"):
        self._config_name = config_name
        self._default_config = getattr(Defaults, plugin_type, {})
        self._plugin_type = plugin_type
        self.plugin_name = plugin_name
        self._config: Box = self._load_config()
    
    def _load_config(self) -> Box[str, Any]:
        configFile = None
        try:
            
            match self._plugin_type:
                case "apps":
                    configFile = open(f"project://{self._config_name}.toml", encoding="utf-8")
                case "draggable_window" | "overlay_widget":
                    configFile = open(f"plugin://{self.plugin_name}/{self._config_name}.toml", encoding="utf-8")
                case "setting":
                    configFile = io.StringIO()
                case "theme":
                    configFile = open(f"resource://theme/{self.plugin_name}/{self._config_name}.toml", encoding="utf-8")
            return Box(toml.load(configFile))
        except Exception as e:
            print(e)
            return Box(self._default_config)
        finally:
            if configFile is not None:
                configFile.close()
    
    def __getattr__(self, item):
        return getattr(self._config, item)
    
    def reload(self):
        self._config = self._load_config()
    
    def plugin_path(self):
        return self._load_path
    
    @classmethod
    def configApplication(cls):
        return cls("Overlay", "apps")
