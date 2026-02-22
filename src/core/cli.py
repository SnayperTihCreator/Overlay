import ast
import inspect
import logging
from typing import Callable, get_type_hints
from types import GeneratorType
from collections.abc import Sequence

from .common import MetaBaseWidget

logger = logging.getLogger(__name__)


class MetaCliInterface(MetaBaseWidget):
    # noinspection PyProtectedMember
    def __new__(cls, name, bases, namespace, **extra):
        new_class = super().__new__(cls, name, bases, namespace)
        
        if hasattr(new_class, "__init_subclass__"):
            pass
        
        new_class.cliFunction = {}
        
        for base in reversed(new_class.__mro__):
            if hasattr(base, 'cliFunction') and isinstance(base.cliFunction, dict):
                for func_name, func in base.cliFunction.items():
                    if hasattr(func, "_cli_func"):
                        cmd_name = func._cli_func or func_name
                        new_class.cliFunction[cmd_name] = func
        
        for attr_name, attr_value in namespace.items():
            if hasattr(attr_value, "_cli_func"):
                cmd_name = attr_value._cli_func or attr_name
                new_class.cliFunction[cmd_name] = attr_value
        
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
    
    def namespace(self) -> str:
        """
        Generates help text for all commands without using print.
        """
        logger.debug(f"Generating namespace help for {self.__class__.__name__}")
        
        output_lines = []
        for name, func in self.cliFunction.items():
            line = self._formatFunc(name, func)
            output_lines.append(line)
        
        return "\n".join(output_lines)
    
    @staticmethod
    def _formatFunc(name, func: Callable) -> str:
        """
        Returns a formatted string describing the function.
        """
        try:
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            param_strings = []
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                
                param_str = param_name
                
                # Add type hint
                if param_name in type_hints:
                    try:
                        type_name = type_hints[param_name].__name__
                    except AttributeError:
                        type_name = str(type_hints[param_name])
                    param_str += f":{type_name}"
                
                # Add default value
                if param.default != param.empty:
                    default_val = repr(param.default)
                    param_str += f"={default_val}"
                elif param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    pass
                else:
                    # Mark required
                    param_str = rf"\[required] {param_str}"
                
                param_strings.append(param_str)
            
            # Build the main line
            if param_strings:
                params_display = " ".join(param_strings)
                line = f"[bright_blue]{name}[/bright_blue] [green]{params_display}[/green]"
            else:
                line = f"[bright_blue]{name}[/bright_blue]"
            
            # Add documentation if available
            if func.__doc__:
                first_line = func.__doc__.strip().split('\n')[0]
                line += f"\n[bright_black]-[bright_magenta]\\[docs][/bright_magenta] {first_line}[/bright_black]"
            
            return line
        
        except Exception as e:
            logger.error(f"Error formatting help for function '{name}': {e}", exc_info=True)
            return f"[red]Error formatting help for {name}[/red]"
    
    def _getImplFuncRaise(self, name):
        impl = self.cliFunction.get(name, None)
        if impl is None:
            raise NameError(f"Command '{name}' not found")
        return impl
    
    @staticmethod
    def _docs(obj):
        return obj.__docs_inter__ if hasattr(obj, "__docs_inter__") else "Docs not found"
    
    @staticmethod
    def _convert_arg(param: inspect.Parameter, arg: str):
        """Converts string arg to annotated type."""
        target_type = param.annotation
        
        if target_type == inspect.Parameter.empty:
            try:
                return ast.literal_eval(arg)
            except (ValueError, SyntaxError):
                return arg
        
        if target_type == str:
            return arg
        
        if target_type == bool:
            lower = arg.lower()
            if lower in ('true', '1', 'yes', 'y', 'on'): return True
            if lower in ('false', '0', 'no', 'n', 'off'): return False
            return bool(arg)
        
        return target_type(arg)
    
    def runner(self, args: list) -> str:
        """
        Main entry point for CLI commands.
        """
        if not args:
            return self.namespace()
        
        cmd_name = args[0]
        cmd_args = args[1:]
        
        logger.info(f"Executing CLI command: '{cmd_name}' args: {cmd_args}")
        
        try:
            impl = self._getImplFuncRaise(cmd_name)
            
            # Inspect params
            sig = inspect.signature(impl)
            params = list(sig.parameters.values())[1:]  # Skip self
            
            # Convert args
            converted_args = []
            for i, (param, arg) in enumerate(zip(params, cmd_args)):
                converted_args.append(self._convert_arg(param, arg))
            
            # Execute
            result = impl(self, *converted_args)
            
            # Format result
            if isinstance(result, bool):
                return f"[green]{'Done' if result else 'Error'}[/green]"
            
            if result is None:
                return "[yellow]Return NONE[/yellow]"
            
            if (isinstance(result, Sequence) or isinstance(result, GeneratorType)) and not isinstance(result, str):
                return "\n".join(f"* [blue]{el}[/blue] -[white] {self._docs(el)}[/white]" for el in result)
            
            return str(result)
        
        except NameError:
            logger.warning(f"CLI command not found: '{cmd_name}'")
            return f"[red]Command '{cmd_name}' not found[/red]"
        
        except (ValueError, TypeError) as e:
            logger.warning(f"CLI argument error for '{cmd_name}': {e}")
            return f"[red]Argument Error: {e}[/red]"
        
        except Exception as e:
            logger.error(f"CLI execution error in '{cmd_name}': {e}", exc_info=True)
            return f"[red]System Error: {e}[/red]"
    
    @_inner_register()
    def help(self, name: str):
        """Show documentation for a specific command."""
        try:
            impl = self._getImplFuncRaise(name)
            if impl.__doc__:
                return f"[cyan]{impl.__doc__.strip()}[/cyan]"
            return "[yellow]Docs not found[/yellow]"
        except NameError:
            return f"[red]Command '{name}' not found[/red]"


__all__ = ["CLInterface", "MetaCliInterface"]
