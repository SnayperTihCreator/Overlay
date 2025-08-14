from typing import Callable
from functools import cache

from PathControl.platformCurrent import getSystem


class HotkeyManager:
    def __init__(self):
        self._handler = self._create_handler()
    
    @cache
    def _create_handler(self):
        """Создает обработчик в зависимости от ОС."""
        match getSystem():
            case ["win32", _]:
                from .windowsHotkeyHandler import WindowsHotkeyHandler
                return WindowsHotkeyHandler()
            case ["linux", "wayland"]:
                from .waylandHotkeyHandler import WaylandHotkeyHandler
                return WaylandHotkeyHandler()
            case ["linux", "x11"]:
                from .x11HotkeyHandler import X11HotkeyHandler
                return X11HotkeyHandler()
            case [system, window]:
                raise NotImplementedError(f"Unsupported OS: {system}/{window}")
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        """Добавляет горячую клавишу."""
        self._handler.add_hotkey(combo, callback, uname)
    
    def remove_hotkey(self, combo: str, uname: str):
        """Удаляет горячую клавишу."""
        self._handler.remove_hotkey(combo, uname)
    
    def start(self):
        """Запускает обработчик."""
        self._handler.start()
    
    def stop(self):
        """Останавливает обработчик."""
        self._handler.stop()
