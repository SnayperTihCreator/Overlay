from typing import Literal
import io
from typing import Type
import traceback

from attrs import define, field
import toml

from .default_configs import *


@define
class Config:
    """
    Класс для управления конфигурационными файлами различных ресурсов (окна, виджеты, приложения и др.).

    Загружает настройки из TOML‑файлов согласно типу ресурса и схеме конфигурации.
    Поддерживает автоматическое создание дефолтных конфигураций при отсутствии файла.
    """
    
    _resource_name: str = field(alias="resource")
    """
    :ivar _resource_name: Имя ресурса (например, название плагина или приложения).
    :type _resource_name: str
    """
    
    _resource_type: Literal["window", "widget", "apps", "setting", "theme"] = field()
    """
    :ivar _resource_type: Тип ресурса, определяющий путь к конфигурации и схему валидации.
    :type _resource_type: Literal["window", "widget", "apps", "setting", "theme"]
    """
    
    _config_name: str = field(default="config")
    """
    :ivar _config_name: Имя конфигурационного файла (без расширения). По умолчанию — "config".
    :type _config_name: str
    """
    
    _scheme: Type[BaseConfig] = field(default=None, repr=False)
    """
    :ivar _scheme: Класс схемы конфигурации (подкласс BaseConfig). Если не задан, определяется автоматически
                 по `_resource_type`.
    :type _scheme: type[BaseConfig], optional
    """
    
    _config: BaseConfig = field(init=False, repr=False)
    """
    :ivar _config: Экземпляр конфигурации, загруженный по схеме `_scheme`.
    :type _config: BaseConfig
    """
    
    def __attrs_post_init__(self):
        """
        Вызывается после инициализации атрибутов.

        Устанавливает схему конфигурации (если не задана) и загружает настройки из файла.
        """
        if self._scheme is None:
            self._scheme = self.getSchemeConfig(self._resource_type)
        self._config = self._load_config()
    
    @staticmethod
    def getSchemeConfig(resource_type) -> Type[BaseConfig]:
        """
        Возвращает класс схемы конфигурации для указанного типа ресурса.

        :param resource_type: Тип ресурса ("window", "widget", "apps", "theme", "setting").
        :type resource_type: str
        :return: Класс схемы (подкласс BaseConfig).
        :rtype: type[BaseConfig]
        :raises TypeError: Если `resource_type` не поддерживается.
        """
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
                raise TypeError(f"Не известный формат конфигураций - {resource_type}")
    
    def _load_config(self) -> BaseConfig:
        """
        Загружает конфигурацию из файла согласно типу ресурса.

        Если файл не найден (для типа "apps"), создаёт его с дефолтными значениями.
        При ошибках вывода использует дефолтную схему.

        :return: Экземпляр конфигурации, соответствующий схеме `_scheme`.
        :rtype: BaseConfig
        :raises FileNotFoundError: Если файл не найден (кроме случая "apps").
        :raises Exception: Для любых других ошибок (выводится через traceback).
        """
        configFile = None
        try:
            match self._resource_type:
                case "apps":
                    configFile = open(f"qt://app/overlay.toml", encoding="utf-8")
                case "window" | "widget":
                    configFile = open(f"plugin://{self.name}/plugin.toml", encoding="utf-8")
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
    def data(self) -> BaseConfig:
        """
        Возвращает копию текущей конфигурации.

        :return: Экземпляр конфигурации (копия).
        :rtype: BaseConfig
        """
        return self._config.copy()
    
    @property
    def name(self) -> str:
        """
        Возвращает имя ресурса.

        :return: Значение `_resource_name`.
        :rtype: str
        """
        return self._resource_name
    
    @property
    def type(self) -> str:
        """
        Возвращает тип ресурса.

        :return: Значение `_resource_type`.
        :rtype: str
        """
        return self._resource_type
    
    def reload(self):
        """
        Перезагружает конфигурацию из файла, обновляя `_config`.

        Использует `_load_config()` для повторного чтения данных.
        """
        self._config = self._load_config()
    
    @classmethod
    def configApplication(cls) -> "Config":
        """
        Создаёт экземпляр конфигурации для приложения с предустановленными параметрами.

        :return: Объект `Config` с `_resource_name="Overlay"` и `_resource_type="apps"`.
        :rtype: Config
        """
        return cls("Overlay", "apps")
