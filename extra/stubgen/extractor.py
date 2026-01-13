import ast
from typing import Optional, List, Dict, Any


class DeepExtractor(ast.NodeVisitor):
    def __init__(self, target_names: List[str] = None, as_module_class: bool = False):
        self.target_names = target_names or []
        self.as_module_class = as_module_class
        self.results: Dict[str, str] = {}
        self.reexports: Dict[str, tuple] = {}
    
    def _is_magic(self, name: str) -> bool:
        return name.startswith("__") and name.endswith("__")
    
    def _is_private(self, name: str) -> bool:
        if self._is_magic(name):
            return False
        return name.startswith("__")
    
    def _get_annotation(self, node: Optional[ast.AST]) -> str:
        """Извлекает строковое представление аннотации типа."""
        if node is None: return "Any"
        try:
            return ast.unparse(node)
        except:
            return "Any"
    
    def _process_enum_member(self, target_id: str, item: ast.AST) -> str:
        """Форматирует элемент Enum, сохраняя его значение."""
        if isinstance(item, ast.Assign) and item.value:
            return f"    {target_id} = {ast.unparse(item.value)}"
        elif isinstance(item, ast.AnnAssign) and item.value:
            return f"    {target_id} = {ast.unparse(item.value)}"
        return f"    {target_id} = ..."
    
    def _process_attrs_member(self, target_id: str, annotation: str, item: ast.AST) -> str:
        """Обработка полей для attrs/dataclass (сохраняем field(...) или дефолт)."""
        if hasattr(item, 'value') and item.value:
            val_str = ast.unparse(item.value)
            return f"    {target_id}: {annotation} = {val_str}"
        return f"    {target_id}: {annotation} = ..."
    
    def _process_standard_member(self, target_id: str, annotation: str) -> str:
        """Обработка обычного атрибута класса для заглушки."""
        return f"    {target_id}: {annotation} = ..."
    
    def _format_arg(self, arg_node: ast.arg, default_node: ast.AST = None) -> str:
        """Форматирует аргумент функции с учетом аннотации и значения по умолчанию."""
        name = arg_node.arg
        annotation = self._get_annotation(arg_node.annotation) if arg_node.annotation else None
        res = name
        if annotation:
            res += f": {annotation}"
        if default_node:
            res += f" = {ast.unparse(default_node)}"
        return res
    
    def _extract_self_attributes(self, init_node: ast.FunctionDef, existing_names: set) -> List[str]:
        """Собирает атрибуты, определенные через self в __init__."""
        attrs = []
        for stmt in init_node.body:
            target_attr = None
            annotation = "Any"
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
                        target_attr = t.attr
            elif isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value,
                                                                         ast.Name) and stmt.target.value.id == "self":
                    target_attr = stmt.target.attr
                    annotation = self._get_annotation(stmt.annotation)
            
            if target_attr and not self._is_private(target_attr) and target_attr not in existing_names:
                attrs.append(f"    {target_attr}: {annotation} = ...")
                existing_names.add(target_attr)
        return attrs
    
    def format_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef, indent: str = "") -> str:
        """Генерирует сигнатуру функции без реализации."""
        decorators = []
        if self.as_module_class:
            decorators.append(f"{indent}@staticmethod")
        for dec in node.decorator_list:
            try:
                name = ast.unparse(dec)
                if any(d in name for d in ("staticmethod", "classmethod", "property")):
                    decorators.append(f"{indent}@{name}")
            except:
                continue
        
        dec_str = "\n".join(decorators) + ("\n" if decorators else "")
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        
        args_obj = node.args
        all_args = []
        
        # Python 3.11/3.8+ Позиционные аргументы (/)
        if hasattr(args_obj, 'posonlyargs') and args_obj.posonlyargs:
            for arg in args_obj.posonlyargs: all_args.append(self._format_arg(arg))
            all_args.append("/")
        
        # Обычные аргументы
        defaults = args_obj.defaults
        padding = [None] * (len(args_obj.args) - len(defaults))
        for arg, d in zip(args_obj.args, padding + list(defaults)):
            all_args.append(self._format_arg(arg, d))
        
        # *args и Keyword-only
        if args_obj.vararg:
            all_args.append(f"*{self._format_arg(args_obj.vararg)}")
        elif args_obj.kwonlyargs:
            all_args.append("*")
        
        for arg, d in zip(args_obj.kwonlyargs, args_obj.kw_defaults):
            all_args.append(self._format_arg(arg, d))
        
        # **kwargs
        if args_obj.kwarg:
            all_args.append(f"**{self._format_arg(args_obj.kwarg)}")
        
        ret = self._get_annotation(node.returns) if node.returns else "Any"
        return f"{dec_str}{indent}{prefix}def {node.name}({', '.join(all_args)}) -> {ret}:\n{indent}    ..."
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Анализирует определение класса и выбирает стратегию обработки атрибутов."""
        if self._is_private(node.name) and node.name not in self.target_names:
            return
        
        # Определяем тип класса
        is_enum = any("Enum" in ast.unparse(b) for b in node.bases)
        is_attrs = any(any(x in ast.unparse(d) for x in ("define", "attr.s", "dataclass"))
                       for d in node.decorator_list)
        
        bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})" if node.bases else ""
        class_decorators = [f"@{ast.unparse(d)}" for d in node.decorator_list]
        
        if self.as_module_class or node.name in self.target_names:
            class_body = []
            known_names = set()
            doc = ast.get_docstring(node)
            
            for item in node.body:
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and not self._is_private(target.id):
                            known_names.add(target.id)
                            
                            # Выбор метода обработки
                            if is_enum:
                                class_body.append(self._process_enum_member(target.id, item))
                            else:
                                anno = self._get_annotation(getattr(item, 'annotation', None))
                                if is_attrs:
                                    class_body.append(self._process_attrs_member(target.id, anno, item))
                                else:
                                    class_body.append(self._process_standard_member(target.id, anno))
            
            # Атрибуты из __init__
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    class_body.extend(self._extract_self_attributes(item, known_names))
            
            # Методы
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not self._is_private(item.name) or item.name == "__init__":
                        class_body.append("    " + self.format_func(item).replace("\n", "\n    "))
            
            # Сборка финального блока
            res = "\n".join(class_decorators) + ("\n" if class_decorators else "")
            res += f"class {node.name}{bases_str}:\n"
            if doc: res += f'    """{doc}"""\n'
            res += "\n".join(class_body) if class_body else "    ..."
            self.results[node.name] = res
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Обработка обычных функций."""
        if not self._is_private(node.name):
            if self.as_module_class or node.name in self.target_names:
                self.results[node.name] = self.format_func(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Отслеживание реэкспорта имен."""
        if any(alias.name == "*" for alias in node.names):
            self.reexports["*"] = (node.module, "*", node.level)
        else:
            for alias in node.names:
                name = alias.asname or alias.name
                self.reexports[name] = (node.module, alias.name, node.level)
    
    def visit_Assign(self, node: ast.Assign):
        """Обработка констант на уровне модуля."""
        if self.as_module_class:
            for target in node.targets:
                if isinstance(target, ast.Name) and not self._is_private(target.id):
                    self.results[target.id] = f"    {target.id}: Any = ..."