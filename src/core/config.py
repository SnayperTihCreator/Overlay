from __future__ import annotations
import logging
import io
from typing import Literal, Type, TypeVar, Generic

from attrs import define, field
import toml

from .default_configs import *

# Setup logger
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseConfig)


@define
class Config(Generic[T]):
    """
    Class for managing configuration files of various resources.
    Supports strict typing via Generics.
    """
    
    _resource_name: str = field(alias="resource")
    _resource_type: Literal["window", "widget", "apps", "setting", "theme"] = field()
    _config_name: str = field(default="config")
    
    _scheme: Type[T] = field(default=None, repr=False)
    _config: T = field(init=False, repr=False)
    
    def __attrs_post_init__(self):
        if self._scheme is None:
            self._scheme = self.getSchemeConfig(self._resource_type)
        self.reload()
    
    @staticmethod
    def getSchemeConfig(resource_type: str) -> Type[T]:
        match resource_type:
            case "window" | "widget":
                return PluginConfig
            case "apps":
                return AppConfig
            case "theme":
                return ThemeConfig
            case "setting":
                return BaseConfig
            case _:
                msg = f"Unknown config format: {resource_type}"
                logger.error(msg)
                raise TypeError(msg)
    
    def _load_config(self) -> T:
        """Loads configuration using (modified) open function."""
        configFile = None
        
        logger.debug(f"Loading config: {self._resource_name} (type: {self._resource_type})")
        
        try:
            match self._resource_type:
                case "apps":
                    configFile = open("qt://app/overlay.toml", encoding="utf-8")
                case "window" | "widget":
                    configFile = open(f"plugin://{self.name}/plugin.toml", encoding="utf-8")
                case "setting":
                    configFile = io.StringIO()
                case "theme":
                    configFile = open(f"resource://theme/{self.name}/{self._config_name}.toml", encoding="utf-8")
            
            data = toml.load(configFile)
            logger.info(f"Config loaded successfully: {self._resource_name}")
            return self._scheme(**data)
        
        except FileNotFoundError as e:
            if self._resource_type == "apps":
                logger.warning(f"App config not found. Creating default: {self._config_name}")
                
                try:
                    with open(f"project://configs/{self._config_name}.toml", "w", encoding="UTF-8") as file:
                        # Serialize default scheme
                        default_instance = self._scheme()
                        default_data = default_instance.model_dump() if hasattr(default_instance, 'model_dump') else {}
                        toml.dump(default_data, file)
                    
                    return self._scheme()
                except Exception as write_err:
                    logger.error(f"Failed to write default config: {write_err}", exc_info=True)
                    return self._scheme()
            
            logger.warning(f"Config file not found for: {self._resource_name}")
            raise e
        
        except Exception as e:
            logger.error(f"Failed to load config '{self._resource_name}': {e}", exc_info=True)
            return self._scheme()
        
        finally:
            if configFile is not None:
                configFile.close()
    
    @property
    def data(self) -> T:
        """Returns the config instance maintaining type T."""
        return self._config
    
    @property
    def name(self) -> str:
        return self._resource_name
    
    @property
    def type(self) -> str:
        return self._resource_type
    
    def reload(self):
        """Reloads data from file."""
        logger.debug(f"Reloading config for {self.name}...")
        self._config = self._load_config()
    
    @classmethod
    def configApplication(cls) -> Config[AppConfig]:
        """Factory method for Application config."""
        return cls("Overlay", "apps")