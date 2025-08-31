from typing import Optional
import uuid
import re

from PySide6.QtCore import QEvent, QCoreApplication, QObject, QDir
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget
from jinja2 import Environment, Template, ChoiceLoader
from attrs import define, field
from fs import open_fs
from fs.subfs import SubFS
from fs import errors, path as fs_path
import toml

from PathControl.jloader import FSLoader
from PathControl import getAppPath
from ColorControl.theme import Theme

qApp: QApplication


class MetaSingtools(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


@define
class ResourceBuilder:
    mainColorIcon: str = field()
    altColorIcon: str = field()
    
    paths: dict[str, str] = field(factory=dict, init=False, repr=False)
    _cache: SubFS = field(default=None, init=False, repr=False)
    
    def __attrs_post_init__(self):
        project = open_fs("project://")
        self._cache = project.makedir(".cache", recreate=True).makedir("theme", recreate=True)
        QDir.addSearchPath("icon", self._cache.getospath(""))
    
    def builder(self, mainColor: QColor, altColor: QColor):
        try:
            data_file = self._cache.readtext("theme_cache.toml")
            data = toml.loads(data_file)
            if data["main_color"] != mainColor.name(QColor.NameFormat.HexRgb) or \
                    data["alt_color"] != altColor.name(QColor.NameFormat.HexRgb):
                self._create_cache(mainColor, altColor)
        except errors.ResourceNotFound:
            self._create_cache(mainColor, altColor)
    
    def _create_cache(self, mainColor: QColor, altColor: QColor):
        data = {
            "main_color": mainColor.name(QColor.NameFormat.HexRgb),
            "alt_color": altColor.name(QColor.NameFormat.HexRgb)
        }
        self._cache.writetext("theme_cache.toml", toml.dumps(data))
        icons = ThemeController().currentTheme.getIconTheme
        
        context = [
            ("main", mainColor)
        ]
        
        for path, color in context:
            self._cache.makedir(path, recreate=True)
            for path_icon in icons:
                content = open(path_icon, "r", encoding="utf-8").read()
                nameFile = fs_path.basename(path_icon)
                content_file = self._replaceColors(content, color, altColor)
                self._cache.writetext(f"{path}/{nameFile}", content_file)
    
    def _replaceColors(self, content: str, color1: QColor, color2: QColor) -> str:
        content1 = re.sub(r"#0{6}", "#"+"0" * 8, content)
        content2 = re.sub(self.mainColorIcon, color1.name(QColor.NameFormat.HexRgb), content1)
        return re.sub(self.altColorIcon, color2.name(QColor.NameFormat.HexRgb), content2)
    
    def register(self, name, path):
        self.paths[name] = path


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


@define
class WidgetIcon:
    widget: QWidget
    path: str
    typeImage: str
    isQrc: bool
    nameMethod: str = "setIcon"
    
    def setImage(self, image):
        method = getattr(self.widget, self.nameMethod)
        method(image)


class ThemeController(metaclass=MetaSingtools):
    @staticmethod
    def __opacity(color: QColor, value: int):
        colorHex = color.name(QColor.NameFormat.HexRgb).strip("#")
        return f"#{value:02x}{colorHex}"
    
    @staticmethod
    def __color(color: QColor):
        return color.name(QColor.NameFormat.HexRgb)
    
    def __image(self, name):
        if self.currentTheme is None: return
        return f"url({self.currentTheme.getImage(name)})"
    
    def __init__(self):
        self.env = Environment(loader=FSLoader("qt://root/css"))
        self.resource_builder = ResourceBuilder("#ff0000", "#00ff00")
        
        self.env.filters["opacity"] = self.__opacity
        self.env.filters["color"] = self.__color
        self.env.filters["image"] = self.__image
        
        self.app_template = self.env.get_template("app/main.css")
        self.currentTheme: Optional[Theme] = None
        self.interface: dict[str, InterfaceStyle] = {}
        self.widgets: dict[int, WidgetIcon] = {}
    
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
    
    def updateImage(self):
        for widgetImage in self.widgets.values():
            self.updateWidget(widgetImage.widget)
    
    def updateAll(self):
        self.updateApp()
        self.update()
        self.updateImage()
    
    def updateWidget(self, widget: QWidget | QObject):
        widgetImage = self.widgets[id(widget)]
        image = self.getImage(widgetImage.path, widgetImage.typeImage, widgetImage.isQrc)
        widgetImage.setImage(image)
    
    def getImage(self, path: str, typeImage: str = "pixmap", isQt=False):
        if self.currentTheme is None: return
        if isQt:
            return self.currentTheme.getModulateImageQt(path, typeImage)
        return self.currentTheme.getModulateImage(path, typeImage)
    
    def getPathImage(self, name):
        if self.currentTheme is None: return
        return self.currentTheme.getImage(name)
    
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
        self.resource_builder.builder(self.currentTheme.mainText, self.currentTheme.altText)
        self.updateAll()
        
        paletteChange = QEvent(QEvent.Type.ApplicationPaletteChange)
        QCoreApplication.postEvent(QCoreApplication.instance(), paletteChange)
    
    def themeName(self):
        if self.currentTheme is None: return
        
        return self.currentTheme.themeName
    
    def registerWidget(self, widget: QWidget | QObject, path: str, nameMethod: str = "setIcon",
                       typeImage: str = "pixmap",
                       isQt=False):
        widgetImage = WidgetIcon(
            widget, path, typeImage, isQt, nameMethod
        )
        self.widgets[id(widget)] = widgetImage
