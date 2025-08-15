from API.CLI import CLInterface

from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
from PathControl.themeLoader import ThemeLoader


class ThemeCLI(CLInterface):
    def __init__(self, themeLoader: ThemeLoader):
        self.loader = themeLoader
        self.defaultTheme = DefaultTheme()
        
        self.cache = {}
        
    @CLInterface.register()
    def action_change(self, name: str):
        if name in self.cache:
            theme = self.cache[name]
        else:
            themeType = self.loader.loadTheme(name)
            theme = themeType()
            self.cache[name] = theme
        ThemeController().setTheme(theme)
        return True
        
    @CLInterface.register()
    def action_list(self):
        return " ".join(self.loader.list())
    
    @CLInterface.register()
    def action_default_change(self):
        ThemeController().setTheme(self.defaultTheme)
        return True
