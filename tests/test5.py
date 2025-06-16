import os
import ast
import sys
import importlib.util
from pathlib import Path
import subprocess
import json
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional
from APIService.tools_folder import ToolsIniter

ToolsIniter("tools").load()


def is_std_lib_module(module_name: str) -> bool:
    """Проверяет, является ли модуль частью стандартной библиотеки Python"""
    if module_name in sys.builtin_module_names:
        return True
    
    root_module = module_name.split('.')[0]
    if root_module in sys.builtin_module_names:
        return True
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        stdlib_paths = {
            os.path.normpath(path)
            for path in sys.path
            if 'site-packages' not in path and 'dist-packages' not in path
        }
        
        if spec.origin is None:
            return True
        
        module_path = os.path.normpath(os.path.dirname(spec.origin))
        return any(
            module_path.startswith(os.path.normpath(stdlib_path))
            for stdlib_path in stdlib_paths
        )
    except (ImportError, AttributeError):
        return False


def get_package_name(module_name: str) -> Optional[str]:
    """Пытается найти имя пакета для модуля"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            # Для пакетов в site-packages
            if 'site-packages' in spec.origin:
                path_parts = spec.origin.split('site-packages')[-1].split(os.sep)
                if len(path_parts) > 1:
                    return path_parts[1]
            # Для одиночных .py файлов
            return module_name.split('.')[0]
    except (ImportError, AttributeError):
        pass
    return None


def find_all_transitive_dependencies(folder: str) -> Dict[str, Set[str]]:
    """Находит все транзитивные зависимости проекта"""
    # 1. Сначала находим все импорты в коде проекта
    folder = Path(folder)
    direct_imports = set()
    for file in folder.glob("*.py"):
        try:
            data_file = file.read_text("utf-8")
            tree = ast.parse(data_file)
        except SyntaxError:
            continue
        else:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not is_std_lib_module(alias.name):
                            direct_imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    print(node.module, node.names)
                    if node.module and not is_std_lib_module(node.module):
                        direct_imports.add(folder/node.module)
    
    # 2. Преобразуем имена модулей в имена пакетов
    package_queue = deque()
    visited_packages = set()
    package_deps = defaultdict(set)
    
    for module in direct_imports:
        pkg = get_package_name(module)
        if pkg and pkg not in visited_packages:
            package_queue.append(pkg)
            visited_packages.add(pkg)
            
    
    print(package_queue, visited_packages, direct_imports)
    # 3. Рекурсивно находим все зависимости
    # while package_queue:
    #     current_pkg = package_queue.popleft()
    #
    #     # Получаем зависимости текущего пакета
    #     deps = get_package_dependencies(current_pkg)
    #     package_deps[current_pkg] = deps
    #
    #     # Добавляем новые зависимости в очередь
    #     for dep in deps:
    #         if dep not in visited_packages:
    #             visited_packages.add(dep)
    #             package_queue.append(dep)
    
    return package_deps


if __name__ == "__main__":
    project_path = "./plugins/ClockDateWidget/"
    print(f"Анализ зависимостей для проекта: {project_path}")
    
    all_dependencies = find_all_transitive_dependencies(project_path)
    
    print("\nВсе транзитивные зависимости:")
    for package, deps in all_dependencies.items():
        print(f"- {package}")
        if deps:
            print(f"  Зависит от: {', '.join(deps)}")