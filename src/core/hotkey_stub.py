from typing import Callable

from PySide6.QtCore import qInfo

from core.common import BaseHotkeyHandler


class StubHotkey(BaseHotkeyHandler):
    def __init__(self):
        super().__init__()
    
    def start(self): ...
    
    def stop(self): ...
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        qInfo(f"stub add_hotkey {combo}: (uname: {uname})")
    
    def remove_hotkey(self, combo, uname: str):
        qInfo(f"stub remove_hotkey {combo}: {uname}")
