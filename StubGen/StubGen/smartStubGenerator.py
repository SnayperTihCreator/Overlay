import ast
import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .initStubVisitor import InitStubVisitor
from .importUsageAnalyzer import ImportUsageAnalyzer
from .smartStubVisitor import SmartStubVisitor


class SmartStubGenerator:
    def __init__(self):
        self.processed_modules: set[str] = set()
    
    def generate_and_package(self, package_name: str, output_dir: str = None):
        """Генерирует stub-файлы для всего пакета"""
        
        if output_dir is None:
            output_dir = f"{package_name}-stubs"
        
        # Добавляем текущую директорию в sys.path
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Создаем директорию для stub-пакета
        stub_package_dir = Path(output_dir) / f"{package_name}-stubs"
        stub_package_dir.mkdir(parents=True, exist_ok=True)
        
        print(stub_package_dir)
        
        try:
            print(f"Поиск пакета {package_name}...")
            package = self._import_module(package_name)
            
            # Обрабатываем весь пакет рекурсивно
            self._process_package(package_name, package, stub_package_dir)
        
        except ImportError as e:
            print(f"Ошибка импорта пакета {package_name}: {e}")
            self._list_available_modules()
            return
        
        # Создаем файлы пакета
        self._create_package_files(package_name, output_dir, stub_package_dir)
        
        print(f"Stub-пакет создан в: {output_dir}")
        print(f"Для установки: pip install {output_dir}/")
    
    def _process_package(self, package_name: str, package: Any, output_dir: Path):
        """Рекурсивно обрабатывает весь пакет"""
        if package_name in self.processed_modules:
            return
        
        self.processed_modules.add(package_name)
        print(f"Обработка: {package_name}")
        
        # Получаем путь к пакету
        package_path = self._get_package_path(package)
        
        # Обрабатываем основной модуль пакета
        main_stub = self._generate_module_stub(package_name, package_path, is_init=True)
        (output_dir / "__init__.pyi").write_text(main_stub, encoding='utf-8')
        
        # Рекурсивно обрабатываем подмодули
        if package_path and os.path.isdir(package_path):
            for item in os.listdir(package_path):
                item_path = os.path.join(package_path, item)
                
                if item.endswith('.py') and item != '__init__.py':
                    # Python файл
                    submodule_name = f"{package_name}.{item[:-3]}"
                    self._process_python_file(submodule_name, item_path, output_dir)
                
                elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '__init__.py')):
                    # Подпакет
                    subpackage_name = f"{package_name}.{item}"
                    try:
                        subpackage = importlib.import_module(subpackage_name)
                        subpackage_dir = output_dir / item
                        subpackage_dir.mkdir(exist_ok=True)
                        self._process_package(subpackage_name, subpackage, subpackage_dir)
                    except ImportError as e:
                        print(f"  Не удалось обработать подпакет {subpackage_name}: {e}")
    
    def _process_python_file(self, module_name: str, file_path: str, output_dir: Path):
        """Обрабатывает отдельный Python файл"""
        try:
            stub_content = self._generate_stub_from_file(module_name, file_path)
            stub_file = output_dir / f"{Path(file_path).stem}.pyi"
            stub_file.write_text(stub_content, encoding='utf-8')
            print(f"  Создан: {stub_file.name}")
        except Exception as e:
            print(f"  Ошибка обработки {module_name}: {e}")
    
    def _generate_module_stub(self, module_name: str, package_path: str = None, is_init: bool = False) -> str:
        """Генерирует stub для модуля"""
        try:
            source_code = self._get_module_source(module_name, package_path)
            if source_code:
                return self._generate_stub_from_source(source_code, module_name, package_path, is_init)
        except Exception as e:
            print(f"    Ошибка генерации stub для {module_name}: {e}")
        
        return ""
    
    def _generate_stub_from_source(self, source_code: str, module_name: str, package_path: str = None,
                                   is_init: bool = False) -> str:
        """Генерирует stub из исходного кода"""
        try:
            tree = ast.parse(source_code)
            
            if is_init:
                # Для __init__.py - не фильтруем импорты
                visitor = InitStubVisitor(module_name, package_path)
            else:
                # Для обычных модулей - используем умную фильтрацию
                usage_analyzer = ImportUsageAnalyzer()
                usage_analyzer.visit(tree)
                visitor = SmartStubVisitor(module_name, package_path, usage_analyzer)
            
            visitor.visit(tree)
            return visitor.get_stub_code()
        except Exception as e:
            print(f"    Ошибка AST парсинга {module_name}: {e}")
            return f"# Ошибка генерации stub для {module_name}\n"
    
    def _generate_stub_from_file(self, module_name: str, file_path: str) -> str:
        """Генерирует stub из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            # Определяем, является ли файл __init__.py
            is_init = Path(file_path).name == '__init__.py'
            return self._generate_stub_from_source(source_code, module_name, os.path.dirname(file_path), is_init)
        except Exception as e:
            return f"# Ошибка чтения {file_path}\n"
    
    def _get_module_source(self, module_name: str, package_path: str = None) -> Optional[str]:
        """Получает исходный код модуля"""
        try:
            if package_path:
                init_file = os.path.join(package_path, "__init__.py")
                if os.path.exists(init_file):
                    with open(init_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
            module_file = f"{module_name.replace('.', '/')}.py"
            if os.path.exists(module_file):
                with open(module_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            return None
        except:
            return None
    
    def _get_package_path(self, package: Any) -> Optional[str]:
        """Получает путь к пакету"""
        if hasattr(package, '__file__') and package.__file__:
            return os.path.dirname(package.__file__)
        return None
    
    def _import_module(self, module_name: str) -> Any:
        """Импортирует модуль"""
        try:
            return importlib.import_module(module_name)
        except ImportError:
            if os.path.exists(f"{module_name}.py"):
                spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            elif os.path.exists(module_name) and os.path.isdir(module_name):
                init_file = os.path.join(module_name, "__init__.py")
                if os.path.exists(init_file):
                    spec = importlib.util.spec_from_file_location(module_name, init_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
            raise
    
    def _list_available_modules(self):
        """Показывает доступные модули"""
        print("\nДоступные модули в текущей директории:")
        for item in Path(".").iterdir():
            if item.suffix == '.py' and item.stem != '__init__':
                print(f"  - {item.stem}")
            elif item.is_dir() and (item / "__init__.py").exists():
                print(f"  - {item.name} (пакет)")
    
    def _create_package_files(self, package_name: str, output_dir: str, stub_package_dir: Path):
        """Создает необходимые файлы пакета"""
        stub_package_name = f"{package_name}-stubs"
        
        # Создаем py.typed
        (stub_package_dir / "py.typed").write_text("", encoding='utf-8')
        
        # setup.py
        setup_content = f'''from setuptools import setup

setup(
    name="{stub_package_name}",
    version="0.1.0",
    packages=["{stub_package_name}"],
    package_data={{
        "{stub_package_name}": ["*.pyi", "**/*.pyi", "py.typed"],
    }},
    include_package_data=True,
    python_requires=">=3.7",
)
'''
        (Path(output_dir) / "setup.py").write_text(setup_content, encoding='utf-8')
        
        # pyproject.toml
        pyproject_content = f'''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{stub_package_name}"
version = "0.1.0"
description = "PEP 561 type stubs for {package_name}"
requires-python = ">=3.7"
'''
        (Path(output_dir) / "pyproject.toml").write_text(pyproject_content, encoding='utf-8')
