import ast
from typing import Optional, List, Dict, Any


class DeepExtractor(ast.NodeVisitor):
    def __init__(self, target_names: List[str] = None, as_module_class: bool = False):
        self.target_names = target_names or []
        self.as_module_class = as_module_class
        self.results: Dict[str, str] = {}
        self.reexports: Dict[str, tuple] = {}  # имя -> (откуда, ориг_имя, уровень)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> str:
        if node is None: return "Any"
        try:
            return ast.unparse(node)
        except:
            return "Any"
    
    def format_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef, indent: str = "") -> str:
        decorators = []
        # Добавляем @staticmethod, если мы превращаем модуль в класс
        if self.as_module_class:
            decorators.append(f"{indent}@staticmethod")
        
        for dec in node.decorator_list:
            try:
                name = ast.unparse(dec)
                if name in ("staticmethod", "classmethod", "property"):
                    decorators.append(f"{indent}@{name}")
            except:
                continue
        
        dec_str = "\n".join(decorators) + ("\n" if decorators else "")
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        
        args = []
        for arg in node.args.args:
            anno = self._get_annotation(arg.annotation)
            args.append(f"{arg.arg}: {anno}" if arg.annotation else arg.arg)
        
        ret = self._get_annotation(node.returns) if node.returns else "Any"
        sig = f"{indent}{prefix}def {node.name}({', '.join(args)}) -> {ret}:"
        
        doc = ast.get_docstring(node)
        body = f'\n{indent}    """{doc}"""\n{indent}    ...' if doc else f"\n{indent}    ..."
        return f"{dec_str}{sig}{body}"
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if not isinstance(node, ast.ImportFrom): return
        
        if any(alias.name == "*" for alias in node.names):
            self.reexports["*"] = (node.module, "*", node.level)
        else:
            for alias in node.names:
                name = alias.asname or alias.name
                self.reexports[name] = (node.module, alias.name, node.level)
                if self.as_module_class:
                    self.results[name] = None
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Поддержка переменных вида CONFIG_VAR: str = "value"
        if self.as_module_class:
            if isinstance(node.target, ast.Name) and not node.target.id.startswith('_'):
                anno = self._get_annotation(node.annotation)
                self.results[node.target.id] = f"    {node.target.id}: {anno} = ..."
    
    def visit_ClassDef(self, node: ast.ClassDef):
        if self.as_module_class or node.name in self.target_names:
            methods = []
            doc = ast.get_docstring(node)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Добавляем 4 пробела к каждой строке отформатированной функции
                    formatted = self.format_func(item)
                    methods.append("    " + formatted.replace("\n", "\n    "))
                elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                    target = item.target if isinstance(item, ast.AnnAssign) else item.targets[0]
                    if isinstance(target, ast.Name):
                        anno = self._get_annotation(getattr(item, 'annotation', None))
                        methods.append(f"    {target.id}: {anno} = ...")
            
            res = f"class {node.name}:\n"
            if doc: res += f'    """{doc}"""\n'
            res += "\n".join(methods) if methods else "    ..."
            self.results[node.name] = res
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.as_module_class or node.name in self.target_names:
            self.results[node.name] = self.format_func(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)
    
    def visit_Assign(self, node: ast.Assign):
        # Если парсим модуль как класс, превращаем глобальные переменные в атрибуты
        if self.as_module_class:
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith('_'):
                    self.results[target.id] = f"    {target.id}: Any = ..."