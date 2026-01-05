from PySide6.QtGui import QColor, QFont
from attrs import define, field

from .base import Theme


@define
class DefaultTheme(Theme):
    baseColor: QColor = field(default=QColor("#6e738d"))
    mainTextColor: QColor = field(default=QColor("#cad3f5"))
    altTextColor: QColor = field(default=QColor("#8aadf4"))
    font: QFont = field(default=QFont("Montserrat", 12, 700))
    
    def preInitTheme(self, *args): ...
    
    def postInitTheme(self, *args): ...
