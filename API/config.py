from typing import Literal
import io
from typing import Any
import traceback

from attrs import define, field
import toml

from .defaultConfigs import *


@define
class Config:
    _resource_name: str = field(alias="resource")
    _resource_type: Literal["window", "widget", "apps", "setting", "theme"] = field()
    _config_name: str = field(default="config")
    
    _scheme: type[BaseConfig] = field(default=None, repr=False)
    _config: BaseConfig = field(init=False, repr=False)
    
    def __attrs_post_init__(self):
        if self._scheme is None:
            self._scheme = self.getSchemeConfig(self._resource_type)
        self._config = self._load_config()
    
    @staticmethod
    def getSchemeConfig(resource_type) -> type[BaseConfig]:
        match resource_type:
            case "window":
                return ConfigWindow
            case "widget":
                return ConfigWidget
            case "apps":
                return ConfigApps
            case "theme":
                return ConfigTheme
            case "setting":
                return BaseConfig
            case _:
                raise TypeError(f"Не известный формат конфигураций - {resource_type}")
    
    def _load_config(self) -> BaseConfig:
        configFile = None
        try:
            match self._resource_type:
                case "apps":
                    configFile = open(f"project://configs/{self._config_name}.toml", encoding="utf-8")
                case "window" | "widget":
                    configFile = open(f"plugin://{self.name}/{self._config_name}.toml", encoding="utf-8")
                case "setting":
                    configFile = io.StringIO()
                case "theme":
                    configFile = open(f"resource://theme/{self.name}/{self._config_name}.toml", encoding="utf-8")
            return self._scheme(**toml.load(configFile))
        except FileNotFoundError as e:
            if self._resource_type == "apps":
                with open(f"project://configs/{self._config_name}.toml", "w", encoding="UTF-8") as file:
                    default = self._scheme().model_dump()
                    toml.dump(default, file)
                return self._scheme()
            raise e
        except Exception as e:
            print(*traceback.format_exception(e))
            return self._scheme()
        finally:
            if configFile is not None:
                configFile.close()
    
    @property
    def data(self):
        return self._config.copy()
    
    @property
    def name(self):
        return self._resource_name
    
    @property
    def type(self):
        return self._resource_type
    
    def reload(self):
        self._config = self._load_config()
    
    @classmethod
    def configApplication(cls):
        return cls("Overlay", "apps")
