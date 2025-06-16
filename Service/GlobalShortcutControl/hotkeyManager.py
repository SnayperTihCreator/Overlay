import platform
import os
from typing import Callable


class HotkeyManager:
    def __init__(self):
        self._handler = self._create_handler()
    
    def _create_handler(self):
        """Создает обработчик в зависимости от ОС."""
        system = platform.system()
        
        if system == "Windows":
            from .windowsHotkeyHandler import WindowsHotkeyHandler
            return WindowsHotkeyHandler()
        
        elif system == "Linux":
            if self.is_wayland():
                from .waylandHotkeyHandler import WaylandHotkeyHandler
                return WaylandHotkeyHandler()
            else:
                from .x11HotkeyHandler import X11HotkeyHandler
                return X11HotkeyHandler()
        raise NotImplementedError(f"Unsupported OS: {system}")
    
    @staticmethod
    def is_wayland():
        """Проверяет, работает ли Wayland."""
        if "XDG_SESSION_TYPE" in os.environ:
            return None
        return os.environ["XDG_SESSION_TYPE"] == "wayland"
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        """Добавляет горячую клавишу."""
        self._handler.add_hotkey(combo, callback, uname)
    
    def remove_hotkey(self, uname: str):
        """Удаляет горячую клавишу."""
        self._handler.remove_hotkey(uname)
    
    def start(self):
        """Запускает обработчик."""
        self._handler.start()
    
    def stop(self):
        """Останавливает обработчик."""
        self._handler.stop()
