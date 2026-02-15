from abc import ABC, abstractmethod
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class BaseHotkeyHandler(ABC):
    def __init__(self):
        self._callbacks = {}  # {"combo": {"uname": callback}}
        self._active = False
    
    @abstractmethod
    def start(self):
        """Запускает обработчик горячих клавиш."""
        pass
    
    @abstractmethod
    def stop(self):
        """Останавливает обработчик."""
        pass
    
    def add_hotkey(self, combo: str, callback: Callable, uname: str):
        """Потокобезопасное добавление горячей клавиши."""
        norm_combo = self._normalize_combo(combo)
        if norm_combo not in self._callbacks:
            self._callbacks[norm_combo] = {}
        self._callbacks[norm_combo][uname] = callback
        logger.info(f"Hotkey added: {combo} (id: {uname})")
    
    def remove_hotkey(self, combo, uname: str):
        """Потокобезопасное удаление горячей клавиши."""
        try:
            norm_combo = self._normalize_combo(combo)
            del self._callbacks[norm_combo][uname]
            logger.info(f"Hotkey removed (id: {uname})")
            
            if not self._callbacks[norm_combo]:
                del self._callbacks[norm_combo]
        
        except KeyError:
            logger.warning(f"Failed to remove hotkey: {combo} (id: {uname}) not found.")
        except Exception as e:
            logger.error(f"Error removing hotkey: {e}", exc_info=True)
    
    def _normalize_combo(self, combo: str) -> str:
        """
        Normalize combo string (lowercase, sorted).
        """
        keys = sorted(k.strip().lower() for k in combo.split('+'))
        return '+'.join(keys)
    
    def _trigger_callbacks(self, combo: str):
        """
        Execute all callbacks for the triggered combo.
        """
        if combo in self._callbacks:
            for uname, callback in self._callbacks[combo].items():
                try:
                    callback(uname)
                except Exception as e:
                    logger.warning(f"Hotkey callback failed for '{uname}': {e}")
                    logger.error("Callback execution error", exc_info=True)