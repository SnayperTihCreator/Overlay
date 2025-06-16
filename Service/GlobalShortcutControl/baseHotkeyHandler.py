from abc import ABC, abstractmethod
from typing import Callable

from PySide6.QtCore import qInfo, qCritical, QObject


class BaseHotkeyHandler:
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
        qInfo(f"Added hotkey: {combo} (uname: {uname})")
    
    def remove_hotkey(self, combo, uname: str):
        """Потокобезопасное удаление горячей клавиши."""
        combo = self._normalize_combo(combo)
        del self._callbacks[combo][uname]
        qInfo(f"Removed hotkey (uname: {uname})")
    
    def _normalize_combo(self, combo: str) -> str:
        """Приводит комбинацию к единому формату (lowercase, sorted)."""
        keys = sorted(k.strip().lower() for k in combo.split('+'))
        return '+'.join(keys)
    
    def _trigger_callbacks(self, combo: str):
        """Вызывает все обработчики для комбинации."""
        if combo in self._callbacks:
            for uname, callback in self._callbacks[combo].items():
                try:
                    callback(uname)
                except Exception as e:
                    qCritical(f"Callback error: {e}")
