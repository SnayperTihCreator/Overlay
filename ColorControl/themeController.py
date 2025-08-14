from typing import Optional
import uuid

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget
from jinja2 import Environment, Template
from attrs import define, field

from PathControl.jloader import FSLoader
from ColorControl.theme import Theme


class MetaSingtools(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


qApp: QApplication


@define
class InterfaceStyle:
    interface: QApplication | QWidget = field()
    env_path: Optional[str] = field(default=None)
    template: Optional[Template] = field(default=None)
    
    def initialized(self, env: Environment):
        if self.template is None:
            self.template = env.get_template(self.env_path)
    
    def render(self, *args, **kwargs):
        return self.template.render(*args, **kwargs)
    
    def initStyleSheet(self, *args, **kwargs):
        css = self.render(*args, **kwargs)
        self.interface.setStyleSheet(css)


class ThemeController(metaclass=MetaSingtools):
    def __init__(self):
        self.env = Environment(loader=FSLoader("qt://root/css"))
        self.app_template = self.env.get_template("app/main.css")
        self.currentTheme: Optional[Theme] = None
        self.interface: dict[str, InterfaceStyle] = {}
    
    def registerApp(self, app: QApplication):
        self.interface["app"] = InterfaceStyle(app, "app/main.css")
    
    def register(self, widget: QWidget, path: str, isEnv=True):
        uid = getattr(widget, "uid", uuid.uuid4().hex)
        if isEnv:
            self.interface[uid] = InterfaceStyle(widget, path)
        else:
            template = Template(open(path, encoding="utf-8").read())
            self.interface[uid] = InterfaceStyle(widget, None, template)
        return uid
    
    def update(self):
        if self.currentTheme is None: return
        
        for name, int_style in self.interface.items():
            if name != "app":
                int_style.initialized(self.env)
                int_style.initStyleSheet(theme=self.currentTheme)
    
    def updateUid(self, uid):
        int_style = self.interface[uid]
        int_style.initialized(self.env)
        int_style.initStyleSheet(theme=self.currentTheme)
    
    def updateApp(self):
        if self.currentTheme is None: return
        
        self.interface["app"].interface.setFont(self.currentTheme.font)
        self.interface["app"].initialized(self.env)
        self.interface["app"].initStyleSheet(theme=self.currentTheme)
    
    def updateAll(self):
        self.updateApp()
        self.update()
    
    def getImage(self, path: str, typeImage: str = "pixmap", isQt=False):
        if self.currentTheme is None: return
        if isQt:
            return self.currentTheme.getModulateImageQt(path, typeImage)
        return self.currentTheme.getModulateImage(path, typeImage)
    
    def color(self, name):
        if self.currentTheme is None: return
        color = getattr(self.currentTheme, name)
        if callable(color):
            color = color()
        
        if isinstance(color, str):
            return QColor(f"#{color}")
        return color
    
    def modulated(self, obj):
        if self.currentTheme is None: return
        
        return self.currentTheme.modulated(obj)
    
    def setTheme(self, theme: Theme):
        self.currentTheme = theme
        self.updateAll()
