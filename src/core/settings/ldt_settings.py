from collections import deque
from pathlib import Path
from typing import Optional, List, Type, Any, Union
from contextlib import contextmanager

from utils.ldt import LDT
from .drivers import BaseDriver


class LDTSettings:
    """
    Полнофункциональная замена QSettings на базе LDT и сменных драйверов.
    Использует collections.deque для эффективного управления стеком групп.
    """
    
    def __init__(self, file_path: Union[str, Path], driver: BaseDriver, ldt_instance: Optional[LDT] = None, preload: bool = True):
        self.path = Path(file_path)
        self.driver = driver
        self.ldt = ldt_instance if ldt_instance else LDT()
        self._group_stack: deque[str] = deque()
        if preload:
            self.load()
    
    # --- Навигация и Группы ---
    
    def beginGroup(self, prefix: str):
        if prefix:
            clean_prefix = prefix.strip('./').replace('/', '.')
            self._group_stack.append(clean_prefix)
    
    def endGroup(self):
        if self._group_stack:
            self._group_stack.pop()
        else:
            print("[LDTSettings] Warning: endGroup() called without matching beginGroup()")
    
    def group(self) -> str:
        """Возвращает текущую активную группу (строкой)"""
        return "/".join(self._group_stack)
    
    @contextmanager
    def group_context(self, prefix: str):
        """Python-style контекстный менеджер для групп"""
        self.beginGroup(prefix)
        try:
            yield self
        finally:
            self.endGroup()
    
    # --- Основные операции с данными ---
    
    def setValue(self, key: str, value: Any):
        full_key = self._get_full_key(key)
        self.ldt.set(full_key, value)
    
    def value(self, key: str, default: Any = None, type_cls: Optional[Type] = None) -> Any:
        full_key = self._get_full_key(key)
        return self.ldt.get(full_key, target_cls=type_cls, default=default)
    
    def contains(self, key: str) -> bool:
        """Проверяет, существует ли ключ или группа"""
        full_key = self._get_full_key(key)
        return self.ldt.get(full_key) is not None
    
    def remove(self, key: str):
        """Удаляет ключ или целую группу"""
        self.ldt.delete(self._get_full_key(key))
    
    def clear(self):
        """Полная очистка конфига"""
        self.ldt.clear()
    
    # --- Инспекция (Методы для итерации) ---
    
    def allKeys(self) -> List[str]:
        """Возвращает список всех ключей в текущей группе (только верхний уровень)"""
        branch = self._get_current_branch()
        if isinstance(branch, dict):
            return [k for k, v in branch.items() if not isinstance(v, dict)]
        return []
    
    def childGroups(self) -> List[str]:
        """Возвращает список имен подгрупп в текущей группе"""
        branch = self._get_current_branch()
        if isinstance(branch, dict):
            return [k for k, v in branch.items() if isinstance(v, dict)]
        return []
    
    def childKeys(self) -> List[str]:
        """Аналог allKeys(), возвращает только ключи (не группы)"""
        return self.allKeys()
    
    # --- Синхронизация ---
    
    def sync(self):
        try:
            # self.path.parent.mkdir(parents=True, exist_ok=True)
            self.driver.write(self.path, self.ldt.to_dict())
        except Exception as e:
            print(f"[LDTSettings] Sync error: {e}")
    
    def load(self):
        if self.path.exists():
            try:
                data = self.driver.read(self.path)
                if isinstance(data, dict | LDT):
                    self.ldt.clear()
                    self.ldt.update(data)
            except Exception as e:
                print(f"[LDTSettings] Load error: {e}")
    
    # --- Внутренние утилиты ---
    
    def _get_full_key(self, key: str) -> str:
        clean_key = key.strip('./').replace('/', '.')
        if not self._group_stack:
            return clean_key
        return f"{'.'.join(self._group_stack)}.{clean_key}"
    
    def _get_current_branch(self) -> Any:
        """Возвращает сырые данные текущей ветки согласно стеку групп"""
        curr = self.ldt.to_dict()
        for g in self._group_stack:
            if isinstance(curr, dict) and g in curr:
                curr = curr[g]
            else:
                return None
        return curr
