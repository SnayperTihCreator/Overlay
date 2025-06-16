from PySide6.QtCore import QObject, QEvent, QKeyCombination
from PySide6.QtGui import QKeyEvent

from KeyCombination import KeyCombination


class GlobalEventFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combs = []

    def registered_handler(self, comb):
        if isinstance(comb, str):
            comb = KeyCombination(comb)
        elif not isinstance(comb, QKeyCombination):
            raise TypeError
        self.combs.append(comb)

    def eventFilter(self, watched, event: QEvent, /):
        if isinstance(event, QKeyEvent):
            if any(comb.check(event) for comb in self.combs):
                return False
            if hasattr(event, "is_global"):
                return True
            return super().eventFilter(watched, event)
        if hasattr(event, "is_global"):
            return True
        return False
