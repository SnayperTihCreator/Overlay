import importlib.abc
import importlib.util
import sys
from core.loaders import OverlayAddonsLoader


class OverlayAddonsImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        self.oloader = OverlayAddonsLoader()
    
    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith("OExtension"):
            return None
        
        parts = fullname.split(".")
        
        spec = importlib.util.spec_from_loader(fullname, self, is_package=True)
        spec.submodule_search_locations = []
        
        return spec
    
    def create_module(self, spec):
        if spec.name == "OExtension":
            if spec.name in sys.modules:
                return sys.modules[spec.name]
            mod = type(sys)(spec.name)
            mod.__path__ = []
            return mod
        
        return self.oloader.import_module(spec.name)
    
    def exec_module(self, module):
        pass


if not any(isinstance(x, OverlayAddonsImporter) for x in sys.meta_path):
    sys.meta_path.insert(0, OverlayAddonsImporter())