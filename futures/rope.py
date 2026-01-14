import asyncio
import functools
import inspect
import weakref
from typing import Any, Callable, Generic, ParamSpec, TypeVar, Type, Union, Optional, Self

P = ParamSpec("P")
R = TypeVar("R")


def support_ropes(cls):
    # Если слотов нет, объект и так поддерживает weakref через __dict__
    if not hasattr(cls, "__slots__"):
        return cls
    
    # Если weakref уже есть в слотах, ничего не делаем
    slots = cls.__slots__
    if "__weakref__" in slots:
        return cls
    
    # Создаем НОВЫЕ слоты
    new_slots = tuple(slots) + ("__weakref__",)
    
    # Собираем словарь атрибутов, исключая те, что Python уже создал для старых слотов
    # (дескрипторы типа <member 'user_id' of 'UserAPI' objects>)
    namespace = {}
    for key, value in cls.__dict__.items():
        if key not in ("__slots__", "__weakref__") and key not in slots:
            namespace[key] = value
    
    # Пересоздаем класс с теми же базами, именем и новыми слотами
    return type(cls.__name__, cls.__bases__, {"__slots__": new_slots, **namespace})


# --- 1. ОБЕРТКИ (WIRE) ---

class BaseWire(Generic[P, R]):
    """Базовая синхронная обертка."""
    
    def __init__(self, func: Callable[P, R], instance: Any, owner: Type, name: str):
        self._func = func
        self._instance = instance
        self._owner = owner
        self._name = name
        functools.update_wrapper(self, func)
    
    def _run_original(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Механика вызова оригинала: учитывает self/cls."""
        if self._instance is not None:
            return self._func(self._instance, *args, **kwargs)
        return self._func(*args, **kwargs)
    
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._run_original(*args, **kwargs)


class AsyncWire(BaseWire[P, R]):
    """
    Правильная асинхронная обертка.
    Возвращает объект корутины, что делает её прозрачной для asyncio.
    """
    
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Any:
        # Мы не делаем __call__ асинхронным, мы возвращаем корутину
        return self._async_wrapper(*args, **kwargs)
    
    async def _async_wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
        # Здесь можно добавить await asyncio.sleep, семафоры и т.д.
        res = self._run_original(*args, **kwargs)
        if inspect.isawaitable(res):
            return await res
        return res


# --- 2. МИКСИНЫ СВЯЗЫВАНИЯ ---

class RopeCoreMixin:
    """Ядро логики: кэширование и инспекция очереди декораторов."""
    
    def _inspect_chain(self, obj: Any):
        """Прошивает цепочку декораторов: staticmethod -> classmethod -> property."""
        if isinstance(obj, staticmethod):
            return 'static', obj.__func__
        if isinstance(obj, classmethod):
            return 'class', obj.__func__
        if isinstance(obj, property):
            return 'property', obj.fget
        return 'method', obj
    
    def _get_wire(self, instance: Any, owner: Type) -> BaseWire:
        # Кэшируем обертку, чтобы сохранять состояние (например, кэш данных)
        key = instance if instance is not None else owner
        if key not in self._wires:
            kind, func = self._inspect_chain(self.raw_func)
            
            actual_func = func
            actual_instance = instance
            
            if kind == 'class':
                # Связываем метод с классом (owner)
                actual_func = func.__get__(None, owner)
                actual_instance = None
            elif kind == 'static':
                actual_instance = None
            
            # Авто-выбор класса обертки, если не задан вручную
            wrapper_cls = self.wire_class
            if wrapper_cls is None:
                wrapper_cls = AsyncWire if inspect.iscoroutinefunction(func) else BaseWire
            
            self._wires[key] = wrapper_cls(
                func=actual_func, instance=actual_instance, owner=owner, name=self.name
            )
        return self._wires[key]


class MethodRopeMixin(RopeCoreMixin):
    def __get__(self, instance, owner):
        return self._get_wire(instance, owner)


class PropertyRopeMixin(RopeCoreMixin):
    def __get__(self, instance, owner):
        if instance is None: return self
        wire = self._get_wire(instance, owner)
        return wire()  # Вызываем сразу для property


# --- 3. ОСНОВНОЙ КЛАСС (SMART ROPE) ---

class SmartRope(MethodRopeMixin):
    def __init__(self, wrapper_class: Optional[Type[BaseWire]] = None):
        self.wire_class = wrapper_class
        self.raw_func = None
        self.name = "unknown"
        # WeakKeyDictionary гарантирует отсутствие утечек памяти даже со __slots__
        self._wires = weakref.WeakKeyDictionary()
    
    def __call__(self, func: Callable) -> Self:
        self.raw_func = func
        # Если декорируем property, меняем миксин на лету
        if isinstance(func, property):
            self.__class__ = type("PropertyRope", (PropertyRopeMixin, SmartRope), {})
        
        functools.update_wrapper(self, func)
        return self
    
    def __set_name__(self, owner, name):
        self.name = name
        if hasattr(owner, '__slots__') and '__weakref__' not in owner.__slots__:
            print(f"WARNING: Class {owner.__name__} uses __slots__ but lacks '__weakref__'. "
                  f"SmartRope might fail.")
    
    # Поддержка Pickle
    def __getstate__(self):
        state = self.__dict__.copy()
        state['_wires'] = None
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._wires = weakref.WeakKeyDictionary()