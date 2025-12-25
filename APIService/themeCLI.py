from functools import lru_cache
from API.cli import CLInterface

from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
from PathControl.themeLoader import ThemeLoader


class ThemeCLI(CLInterface, docs_interface="Протокол для управлениями темами"):
    def __init__(self, themeLoader: ThemeLoader):
        self.loader = themeLoader
        self.defaultTheme = DefaultTheme()
        
    @lru_cache(128)
    def _get_theme_name(self, name):
        themeType = self.loader.loadTheme(name)
        return themeType()
        
    @CLInterface.register()
    def change(self, name: str):
        """
        Изменить тему по названию
        """
        theme = self._get_theme_name(name)
        ThemeController().setTheme(theme)
        return True
        
    @CLInterface.register()
    def list(self):
        """
        Вывести список доступных тем
        """
        return self.loader.list()
    
    @CLInterface.register()
    def default_change(self):
        """
        Установить стандартную тему
        """
        ThemeController().setTheme(self.defaultTheme)
        return True
    
    @CLInterface.register()
    def current(self):
        """
        Получение текущей темы
        """
        return ThemeController().currentTheme.themeName
