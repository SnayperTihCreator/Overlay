import logging
from typing import Callable

from core.common import BaseHotkeyHandler
from .hotkey_stub import StubHotkey
from .errors import OAddonsNotFound

logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self):
        try:
            import OExtension.hotkey as hotkey_module
            self._hotkey_module = hotkey_module
            self._handler = hotkey_module.HotkeyHandler()
            self._hotkey_name = hotkey_module.__name__
            
            logger.info(f"Hotkey manager loaded: {self._hotkey_name}")
        
        except (ImportError, OAddonsNotFound) as e:
            logger.warning(f"Hotkey handler not found: {e}. Using stub.")
            
            self._hotkey_name = "Stub Hotkey"
            self._hotkey_module = None
            self._handler: BaseHotkeyHandler = StubHotkey()
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        """Adds a hotkey binding."""
        self._handler.add_hotkey(combo, callback, uname)
    
    def remove_hotkey(self, combo: str, uname: str):
        """Removes a hotkey binding."""
        self._handler.remove_hotkey(combo, uname)
    
    def start(self):
        """Starts the handler."""
        logger.info(f"Starting hotkey handler: {self._hotkey_name}")
        self._handler.start()
    
    def stop(self):
        """Stops the handler."""
        logger.info(f"Stopping hotkey handler: {self._hotkey_name}")
        self._handler.stop()
