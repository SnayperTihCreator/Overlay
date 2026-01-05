from PySide6.QtCore import Qt, QKeyCombination
from PySide6.QtGui import QKeyEvent


class KeyCombination:
    """
    Класс для работы с комбинациями клавиш, задаваемыми строкой.
    """

    MODIFIERS = {
        "Ctrl": Qt.Modifier.CTRL,
        "Shift": Qt.Modifier.SHIFT,
        "Alt": Qt.Modifier.ALT,
        "Meta": Qt.Modifier.META,
    }

    SPECIAL_KEYS = {
        "Esc": Qt.Key.Key_Escape,
        "Enter": Qt.Key.Key_Return,
        "Tab": Qt.Key.Key_Tab,
        "Space": Qt.Key.Key_Space,
        "Backspace": Qt.Key.Key_Backspace,
        "Delete": Qt.Key.Key_Delete,
        "Insert": Qt.Key.Key_Insert,
        "Home": Qt.Key.Key_Home,
        "End": Qt.Key.Key_End,
        "PageUp": Qt.Key.Key_PageUp,
        "PageDown": Qt.Key.Key_PageDown,
        "Left": Qt.Key.Key_Left,
        "Right": Qt.Key.Key_Right,
        "Up": Qt.Key.Key_Up,
        "Down": Qt.Key.Key_Down,
        "F1": Qt.Key.Key_F1,
        "F2": Qt.Key.Key_F2,
        "F3": Qt.Key.Key_F3,
        "F4": Qt.Key.Key_F4,
        "F5": Qt.Key.Key_F5,
        "F6": Qt.Key.Key_F6,
        "F7": Qt.Key.Key_F7,
        "F8": Qt.Key.Key_F8,
        "F9": Qt.Key.Key_F9,
        "F10": Qt.Key.Key_F10,
        "F11": Qt.Key.Key_F11,
        "F12": Qt.Key.Key_F12,
    }

    def __init__(self, combination: str, _init=True):
        """
        :param combination: Строка с комбинацией, например "Ctrl+Shift+A"
        """
        self.key = None
        self.modifiers = Qt.Modifier(0)
        if _init:
            self._parse_combination(combination)

    def _parse_combination(self, combination: str):
        parts = combination.split("+")

        # Обработка модификаторов
        for part in parts[:-1]:
            mod = self.MODIFIERS.get(part)
            if mod is not None:
                self.modifiers |= mod
            else:
                raise ValueError(f"Unknown modifier: {part}")

        # Обработка основной клавиши
        last_part = parts[-1]

        # Специальные клавиши (F1, Enter и т.д.)
        if last_part in self.SPECIAL_KEYS:
            self.key = self.SPECIAL_KEYS[last_part]
        # Буквы и цифры
        elif len(last_part) == 1:
            self.key = getattr(Qt.Key, f"Key_{last_part.upper()}")
        else:
            raise ValueError(f"Unknown key: {last_part}")

    def check(self, event: QKeyEvent) -> bool:
        """Проверяет, соответствует ли событие клавиатуры этой комбинации."""
        return event.key() == self.key and event.modifiers() == self.modifiers

    @classmethod
    def fromQKeyCombination(cls, comb: QKeyCombination):
        comb2 = cls("", False)
        comb2.key = comb.key()
        comb2.modifiers = comb.keyboardModifiers()
        return comb2
