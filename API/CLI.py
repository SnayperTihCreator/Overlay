from typing import Callable
from io import StringIO
import inspect

from rich import print as rich_print
from PySide6.QtWidgets import QWidget


class MetaCliInterface(type(QWidget)):
    def __new__(cls, name, bases, namespace):
        new_class = super().__new__(cls, name, bases, namespace)
        
        new_class.cliFunction = {}
        
        for attr_name, attr_value in namespace.items():
            if hasattr(attr_value, "_cli_fucn"):
                name = attr_value._cli_fucn or attr_name
                new_class.cliFunction[name] = attr_value
        
        return new_class


class CLInterface(metaclass=MetaCliInterface):
    cliFunction: dict[str, Callable]
    
    @staticmethod
    def register(name=None):
        def wrapper(func):
            func._cli_fucn = name
            return func
        
        return wrapper
    
    def namespace(self):
        output = StringIO()
        for name, func in self.cliFunction.items():
            rich_print(name.strip("action_"), "=:=", file=output, end=" ")
            rich_print(*[param for name, param in inspect.signature(func).parameters.items() if name != "self"],
                       file=output, sep=" | ")
        return output.getvalue()
    
    def runner(self, args) -> str:
        if args:
            impl = self.cliFunction.get(f"action_{args[0]}")
            if impl(self, *args[1:]):
                return "True"
            return "False"
        else:
            return self.namespace()
