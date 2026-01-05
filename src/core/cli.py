import ast
import inspect
import io
from typing import Callable, get_type_hints
from types import GeneratorType
from collections.abc import Sequence

from .common import MetaBaseWidget


class MetaCliInterface(MetaBaseWidget):
    def __new__(cls, name, bases, namespace, **extra):
        new_class = super().__new__(cls, name, bases, namespace)
        new_class.__init_subclass__(**extra)
        
        new_class.cliFunction = {}
        
        for base in reversed(new_class.__mro__):
            if hasattr(base, 'cliFunction') and isinstance(base.cliFunction, dict):
                for func_name, func in base.cliFunction.items():
                    if hasattr(func, "_cli_func"):
                        name = func._cli_func or func_name
                        new_class.cliFunction[name] = func
        
        for attr_name, attr_value in namespace.items():
            if hasattr(attr_value, "_cli_func"):
                name = attr_value._cli_func or attr_name
                new_class.cliFunction[name] = attr_value
        
        return new_class


def _inner_register(name=None):
    def wrapper(func):
        func._cli_func = name
        return func
    
    return wrapper


class CLInterface(metaclass=MetaCliInterface):
    cliFunction: dict[str, Callable]
    
    @staticmethod
    def register(name=None):
        def wrapper(func):
            func._cli_func = name
            return func
        
        return wrapper
    
    def __init_subclass__(cls, **kwargs):
        docs_interface = kwargs.get("docs_interface")
        cls.__docs_inter__ = docs_interface or "[yellow]Docs not found[/yellow]"
    
    def namespace(self):
        stdout = io.StringIO()
        # noinspection PyUnresolvedReferences
        print_manager.disable()
        for name, func in self.cliFunction.items():
            self._formatFunc(name, func, stdout)
        # noinspection PyUnresolvedReferences
        print_manager.enable()
        return stdout.getvalue()
    
    @staticmethod
    def _formatFunc(name, func: Callable, stdout):
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Формируем строку с параметрами
        param_strings = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            param_str = param_name
            
            # Добавляем тип
            if param_name in type_hints:
                type_name = type_hints[param_name].__name__
                param_str += f":{type_name}"
            
            # Добавляем значение по умолчанию
            if param.default != param.empty:
                default_val = repr(param.default)
                param_str += f"={default_val}"
            elif param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                pass  # Не меняем для *args и **kwargs
            else:
                param_str = rf"\[required] {param_str}"
            
            param_strings.append(param_str)
        
        if param_strings:
            params_display = " ".join(param_strings)
            print(f"[bright_blue]{name}[/bright_blue] [green]{params_display}[/green]", file=stdout)
        else:
            print(f"[bright_blue]{name}[/bright_blue]", file=stdout)
        
        if func.__doc__:
            first_line = func.__doc__.strip().split('\n')[0]
            print(rf"[bright_black]-[bright_magenta]\[docs][/bright_magenta] {first_line}[/bright_black]", file=stdout)
    
    def _getImplFuncRaise(self, name):
        impl = self.cliFunction.get(name, None)
        if impl is None:
            raise NameError(f"function <{name}> not found")
        return impl
    
    @staticmethod
    def _docs(obj):
        return obj.__docs_inter__ if hasattr(obj, "__docs_inter__") else "Docs not found"
    
    @staticmethod
    def _convert_arg(param: inspect.Parameter, arg: str):
        """Конвертирует аргумент в тип, указанный в аннотации параметра"""
        param_type = param.annotation
        
        # Если аннотации нет, пытаемся определить тип автоматически
        if param_type == inspect.Parameter.empty:
            try:
                # Пробуем распарсить как литерал Python
                return ast.literal_eval(arg)
            except (ValueError, SyntaxError):
                # Если не получается, возвращаем как есть (уже строка)
                return arg
        
        # Если тип указан и это строка - возвращаем как есть
        if param_type == str:
            return arg
        
        # Для bool обрабатываем специально
        if param_type == bool:
            if arg.lower() in ('true', '1', 'yes', 'y', 'on'):
                return True
            elif arg.lower() in ('false', '0', 'no', 'n', 'off'):
                return False
            else:
                return bool(arg)
        
        # Для других типов вызываем конструктор типа
        return param_type(arg)
    
    def runner(self, args: list) -> str:
        if args:
            impl = self._getImplFuncRaise(args[0])
            # Получаем информацию о параметрах функции
            sig = inspect.signature(impl)
            params = list(sig.parameters.values())[1:]  # Пропускаем self
            
            # Конвертируем аргументы
            converted_args = []
            for i, (param, arg) in enumerate(zip(params, args[1:])):
                try:
                    converted_args.append(self._convert_arg(param, arg))
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Error converting argument '{arg}' to {param.annotation}: {e}")
            
            # Вызываем функцию с конвертированными аргументами
            result = impl(self, *converted_args)
            if isinstance(result, bool):
                return f"[green]{'Done' if result else 'Error'}[/green]"
            if result is None:
                return "[yellow]Return NONE[/yellow]"
            if (isinstance(result, Sequence) or isinstance(result, GeneratorType)) and not isinstance(result, str):
                return "\n".join(f"* [blue]{el}[/blue] -[white] {self._docs(el)}[/white]" for el in result)
            return str(result)
        else:
            return self.namespace()
    
    @_inner_register()
    def help(self, name: str):
        """Полная документация по методу"""
        impl = self._getImplFuncRaise(name)
        if impl.__doc__:
            return f"[cyan]{impl.__doc__.strip()}[/cyan]"
        return "[yellow]Docs not found[/yellow]"


__all__ = ["CLInterface", "MetaCliInterface"]