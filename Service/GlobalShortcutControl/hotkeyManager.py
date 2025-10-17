from typing import Callable

from PySide6.QtCore import qInfo
from Common.baseHotkey import BaseHotkeyHandler
from .stubHotkey import StubHotkey


class HotkeyManager:
    def __init__(self, oaddons_loader, hotkey_name):
        if hotkey_name is None:
            qInfo("not find hotkey handler")
            self._hotkey_name = "stub hotkey"
            self._hotkey_module = None
            self._handler: BaseHotkeyHandler = StubHotkey()
        else:
            qInfo(f"module load {hotkey_name}")
            self._hotkey_name = hotkey_name
            self._hotkey_module = oaddons_loader.import_module(hotkey_name)
            self._handler: BaseHotkeyHandler = self._hotkey_module.HotkeyHandler()
    
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
