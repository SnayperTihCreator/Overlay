import ast


class ImportUsageAnalyzer(ast.NodeVisitor):
    """Анализатор использования импортов"""
    
    def __init__(self):
        self.used_in_annotations: set[str] = set()
        self.used_in_decorators: set[str] = set()
        self.used_in_code: set[str] = set()
        self.all_exports: set[str] = set()
        self.current_context = "code"  # "annotation", "decorator" или "code"
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Анализирует использование в функциях"""
        # Анализируем декораторы
        for decorator in node.decorator_list:
            self.current_context = "decorator"
            self.visit(decorator)
            self.current_context = "code"
        
        # Анализируем аннотации параметров
        for arg in node.args.args:
            if arg.annotation:
                self.current_context = "annotation"
                self.visit(arg.annotation)
                self.current_context = "code"
        
        # Анализируем аннотацию возвращаемого значения
        if node.returns:
            self.current_context = "annotation"
            self.visit(node.returns)
            self.current_context = "code"
        
        # Тело функции - это код
        for item in node.body:
            self.visit(item)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Анализирует использование в асинхронных функциях"""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Анализирует использование в классах"""
        # Анализируем декораторы
        for decorator in node.decorator_list:
            self.current_context = "decorator"
            self.visit(decorator)
            self.current_context = "code"
        
        # Базовые классы - это аннотации
        for base in node.bases:
            self.current_context = "annotation"
            self.visit(base)
            self.current_context = "code"
        
        # Тело класса
        for item in node.body:
            self.visit(item)
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Анализирует аннотированные присваивания"""
        if node.annotation:
            self.current_context = "annotation"
            self.visit(node.annotation)
            self.current_context = "code"
        
        if node.value:
            self.visit(node.value)
    
    def visit_Assign(self, node: ast.Assign):
        """Анализирует присваивания - ищет __all__"""
        if (len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name) and
                node.targets[0].id == '__all__'):
            
            # Обрабатываем __all__
            if isinstance(node.value, ast.List):
                for element in node.value.elts:
                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                        self.all_exports.add(element.value)
                    elif isinstance(element, ast.Str):  # Python <3.8
                        self.all_exports.add(element.s)
        
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name):
        """Анализирует использование имен"""
        if self.current_context == "annotation":
            self.used_in_annotations.add(node.id)
        elif self.current_context == "decorator":
            self.used_in_decorators.add(node.id)
        else:
            self.used_in_code.add(node.id)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Анализирует использование атрибутов"""
        # Для атрибутов в аннотациях и декораторах, сохраняем корневое имя
        if self.current_context in ["annotation", "decorator"]:
            # Ищем корневое имя (первую часть цепочки атрибутов)
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                if self.current_context == "annotation":
                    self.used_in_annotations.add(current.id)
                else:
                    self.used_in_decorators.add(current.id)
        
        # Рекурсивно обходим дальше
        self.generic_visit(node)
