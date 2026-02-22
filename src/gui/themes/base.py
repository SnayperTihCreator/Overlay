from __future__ import annotations
import logging
from abc import ABC, abstractmethod

from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPixmap, QImage
from attrs import define, field

from .colorize import modulateIcon, modulateImage, modulatePixmap

# Initialize logger for this module
logger = logging.getLogger(__name__)


@define
class Theme(ABC):
    font: QFont = field()
    baseColor: QColor = field()
    mainTextColor: QColor = field()
    altTextColor: QColor = field()
    
    themeName: str = field(init=False)
    _imagePaths: dict[str, str] = field(factory=dict, init=False, repr=False)
    _iconsTheme: list[str] = field(factory=list, init=False, repr=False)
    
    def __attrs_pre_init__(self):
        try:
            self.themeName = self.__class__.__name__
            logger.debug(f"Starting pre-init for theme: {self.themeName}")
            
            self.addFontFile(":/base/fonts/Montserrat.ttf")
            self.addFontFile(":/base/fonts/MontserratI.ttf")
            self.addFontFile(":/base/fonts/Uncage-bold.ttf")
            
            self.preInitTheme()
        except Exception as e:
            logger.error(f"Theme pre-initialization failed: {e}", exc_info=True)
    
    def __attrs_post_init__(self):
        try:
            self.addImagePath("UCheckbox", "icon:/main/checkbox_unchecked.svg")
            self.addImagePath("CCheckbox", "icon:/main/checkbox_checked.svg")
            self.addImagePath("UpArrow", "icon:/main/uparrow.svg")
            self.addImagePath("DownArrow", "icon:/main/downarrow.svg")
            self.addImagePath("Overlay", "icon:/main/overlay.svg")
            self.addImagePath("ErrorInspect", "icon:/main/error_inspect.svg")
            
            self.addIconTheme("qt://template/icons/checkbox_checked.svg")
            self.addIconTheme("qt://template/icons/checkbox_unchecked.svg")
            self.addIconTheme("qt://template/icons/uparrow.svg")
            self.addIconTheme("qt://template/icons/downarrow.svg")
            self.addIconTheme("qt://template/icons/overlay.svg")
            self.addIconTheme("qt://template/icons/error_inspect.svg")
            
            self.postInitTheme()
            logger.info(f"Theme '{self.themeName}' initialized successfully")
        except Exception as e:
            logger.error(f"Theme post-initialization failed: {e}", exc_info=True)
    
    @property
    def base(self):
        return self.baseColor
    
    @property
    def mainText(self):
        return self.mainTextColor
    
    @property
    def altText(self):
        return self.altTextColor
    
    def disabledText(self):
        return self.baseColor.lighter(175)
    
    def baseInput(self):
        return self.baseColor.darker(125)
    
    def hovered(self):
        return self.baseColor.lighter(125)
    
    def pressed(self):
        return self.mainTextColor.lighter(125)
    
    def mainSelectText(self):
        return self.altTextColor.lighter(125)
    
    def modulateImage(self):
        return self.mainTextColor
    
    def getModulateImageQt(self, path: str, typeImage: str = "pixmap"):
        try:
            modulate = self.modulateImage()
            match typeImage:
                case "pixmap":
                    return modulatePixmap(QPixmap(path), modulate)
                case "icon":
                    return modulateIcon(QIcon(path), modulate)
                case "image":
                    return modulateImage(QImage(path), modulate)
                case _:
                    logger.warning(f"Unknown image type requested: {typeImage}")
                    return None
        except Exception as e:
            logger.error(f"Failed to modulate QT image ({typeImage}) from '{path}': {e}", exc_info=True)
            return None
    
    def getModulateImage(self, path: str, typeImage: str = "pixmap"):
        try:
            modulate = self.modulateImage()
            
            # Using context manager for safe file reading
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except FileNotFoundError:
                logger.error(f"Image file not found: {path}", exc_info=True)
                return None
            
            match typeImage:
                case "pixmap":
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    return modulatePixmap(pixmap, modulate)
                case "icon":
                    # Recursive call logic from original code, handled implicitly by recursion
                    # We create pixmap first manually to avoid recursion loop if logic was different
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    return modulateIcon(QIcon(pixmap), modulate)
                case "image":
                    image = QImage()
                    image.loadFromData(data)
                    return modulateImage(image, modulate)
                case _:
                    logger.warning(f"Unknown image type requested: {typeImage}")
                    return None
        
        except Exception as e:
            logger.error(f"Failed to modulate image from disk '{path}': {e}", exc_info=True)
            return None
    
    def modulated(self, obj):
        try:
            if isinstance(obj, QIcon):
                return modulateIcon(obj, self.modulateImage())
            elif isinstance(obj, QPixmap):
                return modulatePixmap(obj, self.modulateImage())
            elif isinstance(obj, QImage):
                return modulateImage(obj, self.modulateImage())
            else:
                logger.error(f"Unsupported type for modulation: {type(obj)}")
                raise TypeError("Not modulate image provider")
        except Exception as e:
            logger.error(f"Modulation failed: {e}", exc_info=True)
            # Re-raise explicit TypeError as per business logic, but logged first
            if isinstance(e, TypeError):
                raise e
            return None
    
    @staticmethod
    def addFontFile(path):
        try:
            idx = QFontDatabase.addApplicationFont(path)
            if idx == -1:
                logger.warning(f"Failed to load font from path: {path}")
                return []
            
            families = QFontDatabase.applicationFontFamilies(idx)
            logger.debug(f"Loaded font families: {families}")
            return families
        except Exception as e:
            logger.error(f"Error loading font file '{path}': {e}", exc_info=True)
            return []
    
    def addImagePath(self, name, path):
        self._imagePaths[name] = path
    
    def addIconTheme(self, path):
        self._iconsTheme.append(path)
    
    @property
    def getIconTheme(self):
        return self._iconsTheme.copy()
    
    def getImage(self, name):
        try:
            return self._imagePaths[name]
        except KeyError:
            logger.error(f"Image key not found in theme: {name}", exc_info=True)
            return ""
    
    @abstractmethod
    def preInitTheme(self, *args):
        ...
    
    @abstractmethod
    def postInitTheme(self, *args):
        ...


__all__ = ["Theme"]
