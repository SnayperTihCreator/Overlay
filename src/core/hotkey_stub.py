import logging
from typing import Callable

from core.common import BaseHotkeyHandler

logger = logging.getLogger(__name__)


class StubHotkey(BaseHotkeyHandler):
    def __init__(self):
        super().__init__()
    
    def start(self):
        logger.debug("StubHotkey handler started (inactive).")
    
    def stop(self):
        logger.debug("StubHotkey handler stopped.")
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        logger.info(f"Stub: Mocking hotkey addition: '{combo}' (id: {uname})")
    
    def remove_hotkey(self, combo: str, uname: str):
        logger.info(f"Stub: Mocking hotkey removal: '{combo}' (id: {uname})")