from __future__ import annotations
import logging
from typing import Optional, Dict
import uuid
import re
import toml

from PySide6.QtCore import QEvent, QCoreApplication, QObject, QDir
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget
from jinja2 import Environment, Template, ChoiceLoader
from attrs import define, field
from fs import open_fs
from fs.subfs import SubFS
from fs import errors, path as fs_path

from utils.fs import FSLoader, getAppPath
from .base import Theme

# Initialize logger for this module
logger = logging.getLogger(__name__)

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
    
    paths: Dict[str, str] = field(factory=dict, init=False, repr=False)
    _cache: Optional[SubFS] = field(default=None, init=False, repr=False)
    
    def __attrs_post_init__(self):
        try:
            logger.debug("Initializing ResourceBuilder cache...")
            project = open_fs("project://")
            self._cache = project.makedir(".cache", recreate=True).makedir("theme", recreate=True)
            
            # Register search path for Qt
            cache_path = (getAppPath() / ".cache" / "theme").as_posix()
            QDir.addSearchPath("icon", cache_path)
            logger.debug(f"Added Qt search path 'icon': {cache_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ResourceBuilder: {e}", exc_info=True)
    
    def builder(self, mainColor: QColor, altColor: QColor):
        try:
            data_file = self._cache.readtext("theme_cache.toml")
            data = toml.loads(data_file)
            
            cached_main = data.get("main_color")
            cached_alt = data.get("alt_color")
            
            current_main = mainColor.name(QColor.NameFormat.HexRgb)
            current_alt = altColor.name(QColor.NameFormat.HexRgb)
            
            if cached_main != current_main or cached_alt != current_alt:
                logger.info("Theme colors changed, rebuilding cache...")
                self._create_cache(mainColor, altColor)
            else:
                logger.debug("Theme cache is up to date")
        
        except errors.ResourceNotFound:
            logger.info("Theme cache not found, creating new cache...")
            self._create_cache(mainColor, altColor)
        except Exception as e:
            logger.error(f"Error checking theme cache: {e}", exc_info=True)
            # Try to recreate cache if check failed
            self._create_cache(mainColor, altColor)
    
    def _create_cache(self, mainColor: QColor, altColor: QColor):
        try:
            data = {
                "main_color": mainColor.name(QColor.NameFormat.HexRgb),
                "alt_color": altColor.name(QColor.NameFormat.HexRgb)
            }
            self._cache.writetext("theme_cache.toml", toml.dumps(data))
            
            # Retrieve icons from the current theme (singleton usage implied by original logic)
            theme_controller = ThemeController()
            if not theme_controller.currentTheme:
                logger.warning("Cannot create cache: Current theme is None")
                return
            
            icons = theme_controller.currentTheme.getIconTheme
            context = [("main", mainColor)]
            
            for folder_name, color in context:
                self._cache.makedir(folder_name, recreate=True)
                for path_icon in icons:
                    try:
                        with open(path_icon, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        nameFile = fs_path.basename(path_icon)
                        content_file = self._replaceColors(content, color, altColor)
                        self._cache.writetext(f"{folder_name}/{nameFile}", content_file)
                    except Exception as e:
                        logger.error(f"Failed to process icon '{path_icon}': {e}", exc_info=True)
            
            logger.info("Theme cache created successfully")
        
        except Exception as e:
            logger.error(f"Failed to create cache: {e}", exc_info=True)
    
    def _replaceColors(self, content: str, color1: QColor, color2: QColor) -> str:
        try:
            content1 = re.sub(r"#0{6}", "#" + "0" * 8, content)
            content2 = re.sub(self.mainColorIcon, color1.name(QColor.NameFormat.HexRgb), content1)
            return re.sub(self.altColorIcon, color2.name(QColor.NameFormat.HexRgb), content2)
        except Exception as e:
            logger.error(f"Regex color replacement failed: {e}", exc_info=True)
            return content
    
    def register(self, name, path):
        self.paths[name] = path


@define
class InterfaceStyle:
    interface: QApplication | QWidget = field()
    env_path: Optional[str] = field(default=None)
    template: Optional[Template] = field(default=None)
    
    def initialized(self, env: Environment):
        try:
            if self.template is None and self.env_path:
                self.template = env.get_template(self.env_path)
        except Exception as e:
            logger.error(f"Failed to initialize template '{self.env_path}': {e}", exc_info=True)
    
    def render(self, *args, **kwargs):
        try:
            if self.template:
                return self.template.render(*args, **kwargs)
            return ""
        except Exception as e:
            logger.error(f"Template rendering failed: {e}", exc_info=True)
            return ""
    
    def initStyleSheet(self, *args, **kwargs):
        try:
            css = self.render(*args, **kwargs)
            if css:
                self.interface.setStyleSheet(css)
        except Exception as e:
            logger.error(f"Failed to apply stylesheet: {e}", exc_info=True)


@define
class WidgetIcon:
    widget: QWidget
    path: str
    typeImage: str
    isQrc: bool
    nameMethod: str = "setIcon"
    
    def setImage(self, image):
        try:
            if image is None:
                return
            
            method = getattr(self.widget, self.nameMethod, None)
            if callable(method):
                method(image)
            else:
                logger.warning(f"Widget {self.widget} has no method '{self.nameMethod}'")
        except Exception as e:
            logger.error(f"Failed to set image on widget: {e}", exc_info=True)


class ThemeController(metaclass=MetaSingtools):
    @staticmethod
    def __opacity(color: QColor, value: int):
        try:
            colorHex = color.name(QColor.NameFormat.HexRgb).strip("#")
            return f"#{value:02x}{colorHex}"
        except Exception:
            return "#ff000000"  # Fallback
    
    @staticmethod
    def __color(color: QColor):
        return color.name(QColor.NameFormat.HexRgb)
    
    def __image(self, name):
        if self.currentTheme is None:
            return ""
        return f"url({self.currentTheme.getImage(name)})"
    
    def __init__(self):
        try:
            logger.debug("Initializing ThemeController...")
            
            self.loader = ChoiceLoader([
                FSLoader("qt://root/css"),
                FSLoader("plugin://")
            ])
            self.env = Environment(loader=self.loader)
            self.resource_builder = ResourceBuilder("#ff0000", "#00ff00")
            
            # Register Jinja filters
            self.env.filters["opacity"] = self.__opacity
            self.env.filters["color"] = self.__color
            self.env.filters["image"] = self.__image
            
            self.app_template = None
            try:
                self.app_template = self.env.get_template("app/main.css")
            except Exception as e:
                logger.warning(f"Could not load main app template: {e}")
            
            self.currentTheme: Optional[Theme] = None
            self.interface: Dict[str, InterfaceStyle] = {}
            self.widgets: Dict[int, WidgetIcon] = {}
            
            logger.info("ThemeController initialized")
        
        except Exception as e:
            logger.critical(f"Critical failure initializing ThemeController: {e}", exc_info=True)
    
    def registerApp(self, app: QApplication):
        try:
            self.interface["app"] = InterfaceStyle(app, "app/main.css")
            logger.debug("Registered main application style")
        except Exception as e:
            logger.error(f"Failed to register app: {e}", exc_info=True)
    
    def register(self, widget: QWidget, path: str, isEnv=True):
        try:
            uid = getattr(widget, "uid", uuid.uuid4().hex)
            if isEnv:
                self.interface[uid] = InterfaceStyle(widget, path)
            else:
                parts = path.split("://")
                if len(parts) > 1:
                    real_path = parts[1]
                    template = self.env.get_template(real_path)
                    self.interface[uid] = InterfaceStyle(widget, None, template)
                else:
                    logger.warning(f"Invalid path format for register: {path}")
            
            return uid
        except Exception as e:
            logger.error(f"Failed to register widget style: {e}", exc_info=True)
            return uuid.uuid4().hex
    
    def update(self):
        try:
            if self.currentTheme is None:
                return
            
            for name, int_style in self.interface.items():
                if name != "app":
                    int_style.initialized(self.env)
                    int_style.initStyleSheet(theme=self.currentTheme)
        except Exception as e:
            logger.error(f"Error during update loop: {e}", exc_info=True)
    
    def updateUid(self, uid):
        try:
            if uid in self.interface:
                int_style = self.interface[uid]
                int_style.initialized(self.env)
                int_style.initStyleSheet(theme=self.currentTheme)
            else:
                logger.warning(f"UID not found in interface styles: {uid}")
        except Exception as e:
            logger.error(f"Failed to update UID '{uid}': {e}", exc_info=True)
    
    def updateApp(self):
        try:
            if self.currentTheme is None:
                return
            
            if "app" in self.interface:
                app_style = self.interface["app"]
                app_style.interface.setFont(self.currentTheme.font)
                app_style.initialized(self.env)
                app_style.initStyleSheet(theme=self.currentTheme)
        except Exception as e:
            logger.error(f"Failed to update app style: {e}", exc_info=True)
    
    def updateImage(self):
        try:
            for widgetImage in self.widgets.values():
                self.updateWidget(widgetImage.widget)
        except Exception as e:
            logger.error(f"Failed to update images: {e}", exc_info=True)
    
    def updateAll(self):
        try:
            logger.info("Updating all theme components...")
            self.updateApp()
            self.update()
            self.updateImage()
        except Exception as e:
            logger.error(f"Failed to update all: {e}", exc_info=True)
    
    def updateWidget(self, widget: QWidget | QObject):
        try:
            w_id = id(widget)
            if w_id in self.widgets:
                widgetImage = self.widgets[w_id]
                image = self.getImage(widgetImage.path, widgetImage.typeImage, widgetImage.isQrc)
                widgetImage.setImage(image)
        except Exception as e:
            logger.error(f"Failed to update widget image: {e}", exc_info=True)
    
    def getImage(self, path: str, typeImage: str = "pixmap", isQt=False):
        try:
            if self.currentTheme is None:
                return None
            if isQt:
                return self.currentTheme.getModulateImageQt(path, typeImage)
            return self.currentTheme.getModulateImage(path, typeImage)
        except Exception as e:
            logger.error(f"Failed to get image '{path}': {e}", exc_info=True)
            return None
    
    def getPathImage(self, name):
        try:
            if self.currentTheme is None:
                return None
            return self.currentTheme.getImage(name)
        except Exception as e:
            logger.error(f"Failed to get path image '{name}': {e}", exc_info=True)
            return None
    
    def color(self, name):
        try:
            if self.currentTheme is None:
                return QColor(0, 0, 0)
            
            color = getattr(self.currentTheme, name, None)
            if color is None:
                logger.warning(f"Color '{name}' not found in theme")
                return QColor(0, 0, 0)
            
            if callable(color):
                color = color()
            
            if isinstance(color, str):
                return QColor(color if color.startswith("#") else f"#{color}")
            
            return color
        except Exception as e:
            logger.error(f"Failed to retrieve color '{name}': {e}", exc_info=True)
            return QColor(0, 0, 0)
    
    def modulated(self, obj):
        try:
            if self.currentTheme is None:
                return None
            return self.currentTheme.modulated(obj)
        except Exception as e:
            logger.error(f"Modulation failed: {e}", exc_info=True)
            return None
    
    def setTheme(self, theme: Theme):
        try:
            logger.info(f"Setting theme: {theme.themeName}")
            self.currentTheme = theme
            self.resource_builder.builder(self.currentTheme.mainText, self.currentTheme.altText)
            self.updateAll()
            
            paletteChange = QEvent(QEvent.Type.ApplicationPaletteChange)
            QCoreApplication.postEvent(QCoreApplication.instance(), paletteChange)
            logger.info("Theme set and applied successfully")
        except Exception as e:
            logger.error(f"Failed to set theme: {e}", exc_info=True)
    
    def themeName(self):
        if self.currentTheme is None:
            return None
        return self.currentTheme.themeName
    
    def registerWidget(self, widget: QWidget | QObject, path: str, nameMethod: str = "setIcon",
                       typeImage: str = "pixmap",
                       isQt=False):
        try:
            widgetImage = WidgetIcon(
                widget, path, typeImage, isQt, nameMethod
            )
            self.widgets[id(widget)] = widgetImage
            self.updateWidget(widget)
        except Exception as e:
            logger.error(f"Failed to register widget icon: {e}", exc_info=True)
