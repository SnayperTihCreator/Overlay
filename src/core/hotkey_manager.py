from typing import Callable

from PySide6.QtCore import qInfo
from core.common import BaseHotkeyHandler
from .hotkey_stub import StubHotkey
from .errors import OAddonsNotFound


class HotkeyManager:
    def __init__(self):
        try:
            import OExtension.hotkey as hotkey_module
            self._hotkey_module = hotkey_module
            self._handler = hotkey_module.HotkeyHandler()
            self._hotkey_name = hotkey_module.__name__
            qInfo(f"module load {self._hotkey_name}")
        except (ImportError, OAddonsNotFound) as e:
            print(e)
            qInfo("not find hotkey handler")
            self._hotkey_name = "stub hotkey"
            self._hotkey_module = None
            self._handler: BaseHotkeyHandler = StubHotkey()
    
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
