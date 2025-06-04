from typing import Callable

import keyboard
from .baseHotkeyHandler import BaseHotkeyHandler


class X11HotkeyHandler(BaseHotkeyHandler):
    
    def __init__(self):
        super().__init__()
        self._hotkeys = {}
    
    def start(self):
        if not self._active:
            self._active = True
    
    def stop(self):
        if self._active:
            self._active = False
            keyboard.unhook_all()
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        super().add_hotkey(combo, callback, uname)
        hook = keyboard.add_hotkey(combo, callback, (uname,))
        self._hotkeys[uname] = hook
    
    def remove_hotkey(self, combo, uname: str):
        super().remove_hotkey(combo, uname)
        keyboard.remove_hotkey(self._hotkeys[uname])
        del self._hotkeys[uname]