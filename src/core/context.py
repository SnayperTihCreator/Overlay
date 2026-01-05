from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

_current_plugin = ContextVar("CurrentPlugin", default="App")


def isActiveContextPlugin():
    return _current_plugin.get() != "App"


def innerPlugin(pluginName):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            lastContext = _current_plugin.get()
            _current_plugin.set(pluginName)
            result = func(*args, **kwargs)
            _current_plugin.set(lastContext)
            return result
        
        return inner
    
    return wrapper


def decoPlugin(pluginName):
    def wrapper(cls):
        for name, attr in cls.__dict__.items():
            if callable(attr) and not name.startswith('__'):
                setattr(cls, name, innerPlugin(pluginName)(attr))
        for base in cls.__bases__:
            for name, attr in base.__dict__.items():
                if callable(attr) and name not in cls.__dict__:
                    setattr(cls, name, innerPlugin(pluginName)(attr))
        return cls
    
    return wrapper


@contextmanager
def contextPlugin(pluginName):
    lastContext = _current_plugin.get()
    try:
        _current_plugin.set(pluginName)
        yield
    finally:
        _current_plugin.set(lastContext)
