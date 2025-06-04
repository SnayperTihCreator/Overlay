import importlib
import importlib.util
import sys
import os
from pathlib import Path


def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Не удалось создать спецификацию для {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # Добавляем в кеш модулей
    spec.loader.exec_module(module)
    return module


class Backend:
    def __init__(self, path: Path, name):
        window = os.environ.get("XDG_SESSION_TYPE", "")
        if window:
            window = f"_{window}"
        spec = f"_{name}_{sys.platform}{window}"
        path_spec = str((path / spec).with_suffix(".py"))
        module = load_module_from_file(spec, path_spec)
        self.__dict__ = module.__dict__
