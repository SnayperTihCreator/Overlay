import importlib.abc
import importlib.util
import importlib.machinery
import sys
from PathControl.overlayAddonsLoader import OverlayAddonsLoader


class OverlayAddonsImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        self.oloader = OverlayAddonsLoader()
    
    def find_spec(self, fullname, path, target=...):
        if not fullname.startswith("OExtension"):
            return
        
        root, *name = fullname.split(".")
        
        spec = importlib.util.spec_from_loader(
            ".".join(name) if name else fullname,
            self,
            origin=f"resource://overlay_addons/{'.'.join(name)}",
            is_package=True
        )
        
        spec.loader_state = {
            "not_load": not bool(name)
        }
        
        return spec
    
    def create_module(self, spec):
        if spec.loader_state["not_load"]:
            return
        return self.oloader.import_module(spec.name)
    
    def exec_module(self, module): ...


sys.meta_path.insert(0, OverlayAddonsImporter())
