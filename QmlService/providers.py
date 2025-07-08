from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QPixmap, QColor
from urllib.parse import parse_qs, urlparse

from APIService.colorize import modulatePixmap


class PluginImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Pixmap)
    
    def requestPixmap(self, id, size, requestedSize, /):
        with open(f"plugin://{id}", "rb") as image:
            pixmap = QPixmap()
            pixmap.loadFromData(image.read())
            return pixmap
        
        
class ModulateImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Pixmap)
        
    def requestPixmap(self, id, size, requestedSize):
        url = urlparse(id)
        params = parse_qs(url.query)
        with open(f"""{params.get("scheme", ["qt"])[0]}://{url.path}""", "rb") as image:
            pixmap = QPixmap()
            pixmap.loadFromData(image.read())
            color = QColor(params.get("modulate", ["#000"])[0])
            return modulatePixmap(pixmap, color)
