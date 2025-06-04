from enum import IntEnum, auto

from PySide6.QtCore import Qt

flags = (
    Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.Tool
    | Qt.WindowType.WindowStaysOnTopHint
)


class ItemRole(IntEnum):
    TYPE_NAME = Qt.ItemDataRole.UserRole
    MODULE = auto()
    IS_DUPLICATE = auto()
    COUNT_DUPLICATE = auto()
