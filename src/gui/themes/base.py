from abc import ABC, abstractmethod

from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPixmap, QImage
from attrs import define, field

from .colorize import modulateIcon, modulateImage, modulatePixmap


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
        self.themeName = self.__class__.__name__
        self.addFontFile(":/base/fonts/Montserrat.ttf")
        self.addFontFile(":/base/fonts/MontserratI.ttf")
        self.addFontFile(":/base/fonts/Uncage-bold.ttf")
        self.preInitTheme()
    
    def __attrs_post_init__(self):
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
    
    def modulated(self, obj):
        if isinstance(obj, QIcon):
            return modulateIcon(obj, self.modulateImage())
        elif isinstance(obj, QPixmap):
            return modulatePixmap(obj, self.modulateImage())
        elif isinstance(obj, QImage):
            return modulateImage(obj, self.modulateImage())
        else:
            raise TypeError("Not modulate image provider")
    
    @staticmethod
    def addFontFile(path):
        idx = QFontDatabase.addApplicationFont(path)
        return QFontDatabase.applicationFontFamilies(idx)
    
    def addImagePath(self, name, path):
        self._imagePaths[name] = path
    
    def addIconTheme(self, path):
        self._iconsTheme.append(path)
    
    @property
    def getIconTheme(self):
        return self._iconsTheme.copy()
    
    def getImage(self, name):
        return self._imagePaths[name]
    
    @abstractmethod
    def preInitTheme(self, *args):
        ...
    
    @abstractmethod
    def postInitTheme(self, *args):
        ...


__all__ = ["Theme"]
