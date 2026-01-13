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
        if node is None: return "Any"
        try:
            return ast.unparse(node)
        except:
            return "Any"
    
    def _format_arg(self, arg_node: ast.arg, default_node: ast.AST = None) -> str:
        name = arg_node.arg
        annotation = self._get_annotation(arg_node.annotation) if arg_node.annotation else None
        res = name
        if annotation:
            res += f": {annotation}"
        if default_node:
            res += f" = {ast.unparse(default_node)}"
        return res
    
    def _extract_self_attributes(self, init_node: ast.FunctionDef, existing_names: set) -> List[str]:
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
        if hasattr(args_obj, 'posonlyargs') and args_obj.posonlyargs:
            for arg in args_obj.posonlyargs: all_args.append(self._format_arg(arg))
            all_args.append("/")
        
        defaults = args_obj.defaults
        padding = [None] * (len(args_obj.args) - len(defaults))
        for arg, d in zip(args_obj.args, padding + list(defaults)):
            all_args.append(self._format_arg(arg, d))
        
        if args_obj.vararg:
            all_args.append(f"*{self._format_arg(args_obj.vararg)}")
        elif args_obj.kwonlyargs:
            all_args.append("*")
        
        for arg, d in zip(args_obj.kwonlyargs, args_obj.kw_defaults):
            all_args.append(self._format_arg(arg, d))
        
        if args_obj.kwarg: all_args.append(f"**{self._format_arg(args_obj.kwarg)}")
        
        ret = self._get_annotation(node.returns) if node.returns else "Any"
        return f"{dec_str}{indent}{prefix}def {node.name}({', '.join(all_args)}) -> {ret}:\n{indent}    ..."
    
    def visit_ClassDef(self, node: ast.ClassDef):
        if self._is_private(node.name) and node.name not in self.target_names:
            return
        
        bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})" if node.bases else ""
        class_decorators = []
        is_attrs = False
        for d in node.decorator_list:
            d_str = ast.unparse(d)
            class_decorators.append(f"@{d_str}")
            if any(x in d_str for x in ("define", "attr.s", "dataclass", "mutable", "frozen")):
                is_attrs = True
        
        if self.as_module_class or node.name in self.target_names:
            class_body = []
            known_names = set()
            doc = ast.get_docstring(node)
            
            for item in node.body:
                # Обработка переменных (атрибутов)
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and not self._is_private(target.id):
                            known_names.add(target.id)
                            anno = self._get_annotation(getattr(item, 'annotation', None))
                            
                            # ЛОГИКА ДЛЯ ATTRS: переносим field(...) целиком
                            if is_attrs and hasattr(item, 'value') and item.value:
                                val_str = ast.unparse(item.value)
                                class_body.append(f"    {target.id}: {anno} = {val_str}")
                            else:
                                class_body.append(f"    {target.id}: {anno} = ...")
            
            # Атрибуты из __init__ для обычных классов
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    class_body.extend(self._extract_self_attributes(item, known_names))
            
            # Методы
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not self._is_private(item.name) or item.name == "__init__":
                        class_body.append("    " + self.format_func(item).replace("\n", "\n    "))
            
            res = "\n".join(class_decorators) + ("\n" if class_decorators else "")
            res += f"class {node.name}{bases_str}:\n"
            if doc: res += f'    """{doc}"""\n'
            res += "\n".join(class_body) if class_body else "    ..."
            self.results[node.name] = res
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not self._is_private(node.name):
            if self.as_module_class or node.name in self.target_names:
                self.results[node.name] = self.format_func(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if any(alias.name == "*" for alias in node.names):
            self.reexports["*"] = (node.module, "*", node.level)
        else:
            for alias in node.names:
                name = alias.asname or alias.name
                self.reexports[name] = (node.module, alias.name, node.level)
    
    def visit_Assign(self, node: ast.Assign):
        if self.as_module_class:
            for target in node.targets:
                if isinstance(target, ast.Name) and not self._is_private(target.id):
                    self.results[target.id] = f"    {target.id}: Any = ..."