from functools import wraps
from abc import ABC, abstractmethod

from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPixmap, QImage
from attrs import define, field

from APIService.colorize import modulatePixmap, modulateIcon, modulateImage


def stripColor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, QColor):
            result = result.name(QColor.NameFormat.HexRgb)
        return result.strip("#")
    
    return wrapper


@define
class Theme(ABC):
    font: QFont = field()
    baseColor: QColor = field()
    mainTextColor: QColor = field()
    altTextColor: QColor = field()
    
    _imagePaths: dict[str, str] = field(factory=dict, init=False, repr=False)
    
    def __attrs_pre_init__(self):
        self.addFontFile(":/base/fonts/Montserrat.ttf")
        self.addFontFile(":/base/fonts/MontserratI.ttf")
        self.preInitTheme()
    
    def __attrs_post_init__(self):
        self.addImagePath("UCheckbox", ":/base/icons/u_checkbox.png")
        self.addImagePath("CCheckbox", ":/base/icons/c_checkbox.png")
        self.postInitTheme()
    
    @property
    @stripColor
    def base(self):
        return self.baseColor
    
    @property
    @stripColor
    def mainText(self):
        return self.mainTextColor
    
    @property
    @stripColor
    def altText(self):
        return self.altTextColor
    
    @stripColor
    def disabledText(self):
        return self.baseColor.lighter(175)
    
    @stripColor
    def baseInput(self):
        return self.baseColor.darker(125)
    
    @stripColor
    def hovered(self):
        return self.baseColor.lighter(125)
    
    @stripColor
    def pressed(self):
        return self.mainTextColor.lighter(125)
    
    @stripColor
    def mainSelectText(self):
        return self.altTextColor.lighter(125)
    
    def modulateImage(self):
        return self.mainTextColor
    
    def getModulateImageQt(self, path: str, typeImage: str = "pixmap"):
        modulate = self.modulateImage()
        match typeImage:
            case "pixmap":
                return modulatePixmap(QPixmap(path), modulate)
            case "icon":
                return modulateIcon(QIcon(path), modulate)
            case "image":
                return modulateImage(QImage(path), modulate)
    
    def getModulateImage(self, path: str, typeImage: str = "pixmap"):
        modulate = self.modulateImage()
        data = open(path, "rb").read()
        match typeImage:
            case "pixmap":
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                return modulatePixmap(pixmap, modulate)
            case "icon":
                pixmap = self.getModulateImage(path)
                return modulateIcon(QIcon(pixmap), modulate)
            case "image":
                image = QImage()
                image.loadFromData(data)
                return modulateImage(image, modulate)
    
    @staticmethod
    def addFontFile(path):
        QFontDatabase.addApplicationFont(path)
        # print(QFontDatabase.applicationFontFamilies(idx))
    
    def addImagePath(self, name, path):
        self._imagePaths[name] = path
    
    def getImage(self, name):
        return self._imagePaths[name]
    
    @abstractmethod
    def preInitTheme(self, *args):
        ...
    
    @abstractmethod
    def postInitTheme(self, *args):
        ...


__all__ = ["Theme", "stripColor"]
