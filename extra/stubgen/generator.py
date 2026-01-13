import ast
import logging
from pathlib import Path
from typing import List, Dict
from .extractor import DeepExtractor

logger = logging.getLogger("stubgen")


def resolve_module_file(module_name: str | None, level: int, current_file: Path, src_root: Path) -> Path | None:
    if level > 0:
        base_dir = current_file.parent
        for _ in range(level - 1): base_dir = base_dir.parent
        path = base_dir if not module_name else base_dir.joinpath(*module_name.split('.'))
    else:
        if not module_name: return None
        path = src_root.joinpath(*module_name.split('.'))
    
    # Пакет (__init__.py) всегда важнее одиночного файла
    init_file = path / "__init__.py"
    if init_file.exists(): return init_file
    
    py_file = path.with_suffix('.py')
    if py_file.exists(): return py_file
    
    return None


def process_recursive(module_name: str | None, target_names: List[str], src_root: Path,
                      current_file: Path, level: int = 0, as_class: bool = False) -> Dict[str, str]:
    source_file = resolve_module_file(module_name, level, current_file, src_root)
    if not source_file:
        return {}
    
    logger.info(f"Анализ: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    extractor = DeepExtractor(target_names=target_names, as_module_class=as_class)
    extractor.visit(tree)
    results = extractor.results
    
    # Рекурсивный сбор для '*' (from .module import *)
    if "*" in extractor.reexports:
        sub_mod, _, sub_lvl = extractor.reexports["*"]
        results.update(process_recursive(sub_mod, target_names, src_root, source_file, sub_lvl, as_class))
    
    # Собираем список имен, которые нужно найти (либо те, что помечены None, либо те, что отсутствуют)
    missing = [name for name in target_names if name not in results]
    if as_class:
        # В режиме класса вытягиваем всё, что импортировано в ините и помечено как None
        missing.extend([k for k, v in results.items() if v is None])
    
    for name in missing:
        if name in extractor.reexports:
            sub_mod, orig_name, sub_lvl = extractor.reexports[name]
            # Рекурсивно вытаскиваем тело объекта
            deep_res = process_recursive(sub_mod, [orig_name], src_root, source_file, sub_lvl)
            
            if orig_name in deep_res:
                content = deep_res[orig_name]
                # Корректируем имя, если есть 'as'
                if orig_name != name:
                    content = content.replace(f"class {orig_name}", f"class {name}", 1)
                    content = content.replace(f"def {orig_name}", f"def {name}", 1)
                
                # Если мы внутри сборки модуля-класса, добавляем отступ
                if as_class:
                    results[name] = "    " + content.replace("\n", "\n    ")
                else:
                    results[name] = content
    
    # Очищаем результаты от временных None
    return {k: v for k, v in results.items() if v is not None}


def generate_stub(oapi_path: str) -> str:
    oapi_path = Path(oapi_path).resolve()
    src_root = oapi_path.parent
    
    with open(oapi_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    final_blocks = []
    public_names = []
    
    # 1. Извлекаем __all__
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    public_names = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
    
    # 2. Обрабатываем импорты
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            names = [n.name for n in node.names]
            objects_to_search = []
            
            for name in names:
                # Проверяем, не самостоятельный ли это модуль/пакет (default_configs)
                full_mod_path = f"{node.module}.{name}" if node.module else name
                potential_file = resolve_module_file(full_mod_path, 0, oapi_path, src_root)
                
                if potential_file:
                    logger.info(f"Имя '{name}' определено как пакет/модуль. Генерируем класс.")
                    # Собираем содержимое модуля/пакета
                    mod_res = process_recursive(full_mod_path, [], src_root, oapi_path, as_class=True)
                    
                    # НОВОЕ: Формируем тело класса из результатов или ставим заглушку
                    if mod_res:
                        content = "\n".join(mod_res.values())
                    else:
                        content = "    ..."
                    
                    final_blocks.append(f"class {name}:\n    \"\"\"Module-Class Stub\"\"\"\n{content}")
                    continue  # Пропускаем поиск как объекта, так как мы уже создали класс-модуль
                else:
                    # Если это НЕ файл, только тогда добавляем в список поиска внутри родителя
                    objects_to_search.append(name)
            
            # Ищем оставшиеся объекты (OWidget, BaseHotkeyHandler и т.д.) одним махом
            if objects_to_search and node.module:
                results = process_recursive(node.module, objects_to_search, src_root, oapi_path)
                for obj_name in objects_to_search:
                    if obj_name in results:
                        final_blocks.append(results[obj_name])
                    else:
                        logger.warning(f"Объект '{obj_name}' не найден в {node.module}")
        
        elif isinstance(node, ast.Import):
            for n in node.names:
                mod_res = process_recursive(n.name, [], src_root, oapi_path, as_class=True)
                if mod_res:
                    short_name = n.name.split('.')[-1]
                    content = "\n".join(mod_res.values())
                    final_blocks.append(f"class {short_name}:\n{content}")
    
    header = (
        "from __future__ import annotations\n"
        "from typing import Any, Optional, Union, Callable, Type, Literal, Generic\n"
        "from pathlib import Path\n"
        "import inspect\n\n"
        "from abc import ABC, abstractmethod\n"
        "from enum import *\n"
        "# Внешние зависимости\n"
        "from pydantic import BaseModel\n"
        "from ldt import NexusStore, LDT\n"
        "from attrs import define, field\n"
        "from PySide6.QtWidgets import QWidget, QFormLayout, QApplication\n"
        "from PySide6.QtGui import QColor, QIcon, QPixmap, QImage, QFont\n"
        "from PySide6.QtCore import QObject, QSize, QEvent\n"
        "from PySide6.QtQuickWidgets import QQuickWidget\n"
        "from PySide6.QtQuick import QQuickItem\n"
        "from PySide6.QtQml import QQmlEngine\n\n"
    )
    footer = f"\n\n__all__ = {repr(public_names)}"
    return "".join(header) + "\n\n".join(final_blocks) + footer