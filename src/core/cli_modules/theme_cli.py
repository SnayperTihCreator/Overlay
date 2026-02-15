from functools import lru_cache
import logging

from core.cli import CLInterface
from gui.themes import DefaultTheme, ThemeController
from core.loaders import ThemeLoader

logger = logging.getLogger(__name__)


class ThemeCLI(CLInterface, docs_interface="Протокол для управлениями темами"):
    def __init__(self, themeLoader: ThemeLoader):
        self.loader = themeLoader
        self.defaultTheme = DefaultTheme()
        logger.info("ThemeCLI initialized successfully.")
    
    @lru_cache(128)
    def _get_theme_name(self, name):
        logger.debug(f"Loading theme class: {name}")
        themeType = self.loader.loadTheme(name)
        return themeType()
    
    @CLInterface.register()
    def change(self, name: str):
        """
        Change theme by name
        """
        logger.info(f"Request to change theme to: '{name}'")
        try:
            if name == "DefaultTheme":
                return self.default_change()
            theme = self._get_theme_name(name)
            ThemeController().setTheme(theme)
            logger.info(f"Theme changed to: '{name}'")
            return True
        except Exception as e:
            logger.warning(f"Failed to change theme to '{name}': {e}")
            logger.error("Error in ThemeCLI.change", exc_info=True)
            return False
    
    @CLInterface.register()
    def list(self):
        """
        Вывести список доступных тем
        """
        themes = self.loader.list()
        logger.info(f"Theme list requested. Found: {len(themes)}")
        return themes
    
    @CLInterface.register()
    def default_change(self):
        """
        Установить стандартную тему
        """
        ThemeController().setTheme(self.defaultTheme)
        logger.info("Reset to DefaultTheme.")
        return True
    
    @CLInterface.register()
    def current(self):
        """
        Получение текущей темы
        """
        return ThemeController().currentTheme.themeName
