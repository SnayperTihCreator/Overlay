import ast


class InitStubVisitor(ast.NodeVisitor):
    """Visitor для __init__.py - сохраняет все импорты как есть"""
    
    def __init__(self, module_name: str, package_path: str = None):
        self.module_name = module_name
        self.package_path = package_path
        self.imports: list[str] = []
        self.classes: list[str] = []
        self.functions: list[str] = []
        self.variables: list[str] = []
        self.all_exports: list[str] = []
        self.need_any_import = False
    
    def get_stub_code(self) -> str:
        """Возвращает сгенерированный stub код"""
        lines = []
        
        # Добавляем импорт Any если он нужен
        if self.need_any_import and not any("Any" in imp for imp in self.imports):
            self.imports.insert(0, "from typing import Any")
        
        # В __init__.py сохраняем ВСЕ импорты как есть
        if self.imports:
            lines.extend(self.imports)
        
        if lines:
            lines.append("")
        
        # Добавляем __all__ если есть
        if self.all_exports:
            all_str = ", ".join(f'"{name}"' for name in self.all_exports)
            lines.append(f"__all__ = [{all_str}]")
            lines.append("")
        
        # Добавляем переменные, функции, классы
        all_items = self.variables + self.functions + self.classes
        if all_items:
            lines.extend(all_items)
        
        return "\n".join(lines)
    
    def _should_include_name(self, name: str) -> bool:
        """Определяет, нужно ли включать имя в stub"""
        if name.startswith('_') and not name.startswith('__'):
            return False
        return True
    
    def visit_Import(self, node: ast.Import):
        """Сохраняем все импорты как есть"""
        for alias in node.names:
            if alias.asname:
                self.imports.append(f"import {alias.name} as {alias.asname}")
            else:
                self.imports.append(f"import {alias.name}")
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Сохраняем все импорты как есть"""
        if not node.module:
            return
        
        # Сохраняем относительные импорты как есть
        dots = '.' * node.level
        module_name = f"{dots}{node.module}" if node.module else dots.rstrip('.')
        
        # Формируем список импортов с as
        imports_list = []
        for alias in node.names:
            if alias.asname:
                imports_list.append(f"{alias.name} as {alias.asname}")
            else:
                imports_list.append(alias.name)
        
        if imports_list:
            self.imports.append(f"from {module_name} import {', '.join(imports_list)}")
    
    def visit_Assign(self, node: ast.Assign):
        """Обрабатывает присваивания - ищет __all__"""
        if (len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name) and
                node.targets[0].id == '__all__'):
            
            # Обрабатываем __all__
            if isinstance(node.value, ast.List):
                for element in node.value.elts:
                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                        self.all_exports.append(element.value)
                    elif isinstance(element, ast.Str):  # Python <3.8
                        self.all_exports.append(element.s)
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Обрабатывает аннотированные присваивания"""
        if isinstance(node.target, ast.Name) and self._should_include_name(node.target.id):
            var_name = node.target.id
            annotation = self._get_annotation(node.annotation)
            
            if var_name.isupper() or not node.value:
                self.variables.append(f"{var_name}: {annotation}")
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Обрабатывает классы - СОХРАНЯЕМ ДЕКОРАТОРЫ"""
        if not self._should_include_name(node.name):
            return
        
        # Декораторы класса
        decorators = []
        for decorator in node.decorator_list:
            decorator_str = self._get_decorator(decorator)
            if decorator_str:
                decorators.append("@" + decorator_str)
        
        # Базовые классы
        bases = []
        for base in node.bases:
            base_str = self._get_annotation(base)
            if base_str != "object":
                bases.append(base_str)
        
        base_str = f"({', '.join(bases)})" if bases else ""
        
        # Тело класса
        class_body = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and self._should_include_name(item.name):
                method_str = self._parse_function(item, indent=4)
                if method_str:
                    class_body.append(method_str)
            elif isinstance(item, ast.AsyncFunctionDef) and self._should_include_name(item.name):
                method_str = self._parse_function(item, indent=4, is_async=True)
                if method_str:
                    class_body.append(method_str)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and self._should_include_name(
                    item.target.id):
                # Аннотированные атрибуты класса
                attr_name = item.target.id
                annotation = self._get_annotation(item.annotation)
                class_body.append(f"    {attr_name}: {annotation}")
        
        if not class_body:
            class_body.append("    ...")
        
        # Собираем полное определение класса с декораторами
        class_lines = []
        if decorators:
            class_lines.extend(decorators)
        
        class_lines.append(f"class {node.name}{base_str}:")
        class_lines.extend(class_body)
        
        class_def = "\n".join(class_lines)
        self.classes.append(class_def)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Обрабатывает функции - СОХРАНЯЕМ ДЕКОРАТОРЫ"""
        if not self._should_include_name(node.name):
            return
        
        func_def = self._parse_function(node)
        if func_def:
            self.functions.append(func_def)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Обрабатывает асинхронные функции - СОХРАНЯЕМ ДЕКОРАТОРЫ"""
        if not self._should_include_name(node.name):
            return
        
        func_def = self._parse_function(node, is_async=True)
        if func_def:
            self.functions.append(func_def)
    
    def _parse_function(self, node: ast.FunctionDef, indent: int = 0, is_async: bool = False) -> str:
        """Парсит функцию/метод - СОХРАНЯЕМ ДЕКОРАТОРЫ И ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ"""
        indent_str = " " * indent
        
        # Декораторы функции
        decorators = []
        for decorator in node.decorator_list:
            decorator_str = self._get_decorator(decorator)
            if decorator_str:
                decorators.append(indent_str + "@" + decorator_str)
        
        async_prefix = "async " if is_async else ""
        
        # Параметры
        args = []
        for arg in node.args.args:
            if arg.arg == 'self':
                args.append('self')
                continue
            
            arg_str = arg.arg
            if arg.annotation:
                annotation = self._get_annotation(arg.annotation)
                arg_str = f"{arg.arg}: {annotation}"
            
            # Добавляем значение по умолчанию если есть
            default_index = node.args.args.index(arg) - len(node.args.args) + len(node.args.defaults)
            if 0 <= default_index < len(node.args.defaults):
                default_value = self._get_default_value(node.args.defaults[default_index])
                arg_str += f" = {default_value}"
            
            args.append(arg_str)
        
        # *args
        if node.args.vararg:
            arg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                annotation = self._get_annotation(node.args.vararg.annotation)
                arg_str = f"*{node.args.vararg.arg}: {annotation}"
            args.append(arg_str)
        
        # **kwargs
        if node.args.kwarg:
            arg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                annotation = self._get_annotation(node.args.kwarg.annotation)
                arg_str = f"**{node.args.kwarg.arg}: {annotation}"
            args.append(arg_str)
        
        # Возвращаемое значение
        return_annotation = "Any"
        if node.returns:
            return_annotation = self._get_annotation(node.returns)
        else:
            self.need_any_import = True
        
        # Собираем полное определение функции с декораторами
        func_lines = []
        if decorators:
            func_lines.extend(decorators)
        
        func_lines.append(f"{indent_str}{async_prefix}def {node.name}({', '.join(args)}) -> {return_annotation}: ...")
        
        return "\n".join(func_lines)
    
    def _get_default_value(self, node: ast.AST) -> str:
        """Получает значение по умолчанию"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attr_name(node)
        elif isinstance(node, ast.List):
            elements = [self._get_default_value(el) for el in node.elts]
            return f"[{', '.join(elements)}]"
        elif isinstance(node, ast.Dict):
            items = []
            for key, value in zip(node.keys, node.values):
                key_str = self._get_default_value(key) if key else "None"
                value_str = self._get_default_value(value)
                items.append(f"{key_str}: {value_str}")
            return f"{{{', '.join(items)}}}"
        elif isinstance(node, ast.Tuple):
            elements = [self._get_default_value(el) for el in node.elts]
            return f"({', '.join(elements)})"
        elif isinstance(node, ast.Call):
            func = self._get_default_value(node.func)
            args = [self._get_default_value(arg) for arg in node.args]
            return f"{func}({', '.join(args)})"
        else:
            return "..."
    
    def _get_decorator(self, node: ast.AST) -> str:
        """Получает строковое представление декоратора"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attr_name(node)
        elif isinstance(node, ast.Call):
            # Декоратор с аргументами
            func = self._get_decorator(node.func)
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    args.append(arg.id)
                elif isinstance(arg, ast.Constant):
                    args.append(repr(arg.value))
                else:
                    args.append("...")
            
            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Name):
                    args.append(f"{keyword.arg}={keyword.value.id}")
                elif isinstance(keyword.value, ast.Constant):
                    args.append(f"{keyword.arg}={repr(keyword.value.value)}")
                else:
                    args.append(f"{keyword.arg}=...")
            
            return f"{func}({', '.join(args)})"
        else:
            return "..."
    
    def _get_annotation(self, node: ast.AST) -> str:
        """Извлекает аннотацию типа"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attr_name(node)
        elif isinstance(node, ast.Subscript):
            value = self._get_annotation(node.value)
            if hasattr(node, 'slice'):
                if isinstance(node.slice, ast.Tuple):
                    slices = [self._get_annotation(el) for el in node.slice.elts]
                    slice_str = ", ".join(slices)
                else:
                    slice_str = self._get_annotation(node.slice)
                return f"{value}[{slice_str}]"
            return f"{value}[...]"
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        else:
            self.need_any_import = True
            return "Any"
    
    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Получает полное имя атрибута"""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            prefix = self._get_attr_name(node.value)
            return f"{prefix}.{node.attr}"
        else:
            return node.attr
