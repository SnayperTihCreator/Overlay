from __future__ import annotations
from typing import Literal, Type, TypeVar, Generic
import io
import traceback

from attrs import define, field
import toml

from .default_configs import *

T = TypeVar("T", bound=BaseConfig)


@define
class Config(Generic[T]):
    """
    Класс для управления конфигурационными файлами различных ресурсов.
    Поддерживает строгую типизацию через Generics и Overloads.
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
                raise TypeError(f"Неизвестный формат конфигураций - {resource_type}")
    
    def _load_config(self) -> T:
        """Загружает конфигурацию, используя модифицированный open."""
        configFile = None
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

            return self._scheme(**toml.load(configFile))
        
        except FileNotFoundError as e:
            if self._resource_type == "apps":
                # Создание дефолтного конфига для приложений
                with open(f"project://configs/{self._config_name}.toml", "w", encoding="UTF-8") as file:
                    # Пытаемся вызвать model_dump (Pydantic) или превратить attrs в dict
                    default_data = self._scheme().model_dump() if hasattr(self._scheme, 'model_dump') else {}
                    toml.dump(default_data, file)
                return self._scheme()
            raise e
        except Exception:
            print(f"Ошибка в конфигурации {self._resource_name}:")
            traceback.print_exc()
            return self._scheme()
        finally:
            if configFile is not None:
                configFile.close()
    
    @property
    def data(self) -> T:
        """Возвращает экземпляр конфига с сохранением типа (T)."""
        return self._config
    
    @property
    def name(self) -> str:
        return self._resource_name
    
    @property
    def type(self) -> str:
        return self._resource_type
    
    def reload(self):
        """Перезагружает данные из файла."""
        self._config = self._load_config()
    
    @classmethod
    def configApplication(cls) -> Config[AppConfig]:
        """Фабричный метод для приложения."""
        return cls("Overlay", "apps")
