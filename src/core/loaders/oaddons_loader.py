import os
import zipimport
import re
import sys
from fs import open_fs
from core.errors import OAddonsNotFound, OAddonsInit


class OverlayAddonsLoader:
    def __init__(self):
        self.fs = open_fs("resource://overlay_addons", create=True)
    
    def _find_addon_file(self, addon_name: str) -> str:
        """Ищет .oaddons файл в папке resource."""
        for file in self.fs.listdir(""):
            clean = re.sub(r'(\.oaddons|\[.*?\])', '', file).strip()
            if clean == addon_name:
                return file
        return None
    
    def exists(self, addon_name: str) -> bool:
        return self._find_addon_file(addon_name) is not None
    
    def import_module(self, fullname: str):
        addon_name = fullname.split(".")[-1]
        filename = self._find_addon_file(addon_name)
        
        if not filename:
            raise OAddonsNotFound(fullname)
        
        try:
            zip_path = self.fs.getsyspath(filename)
            if os.name == 'nt' and zip_path.startswith('/'):
                zip_path = zip_path.lstrip('/')
            
            # Твои рабочие фиксы
            inner_path = os.path.join(zip_path, addon_name).replace("\\", "/")
            
            try:
                importer = zipimport.zipimporter(inner_path)
            except zipimport.ZipImportError:
                # Фикс с расширением, который ты нашел
                importer = zipimport.zipimporter(zip_path + ".oaddons")
            
            # Твой фикс с basename
            module = importer.load_module(os.path.basename(zip_path))
            
            # ЕДИНСТВЕННОЕ ДОПОЛНЕНИЕ:
            # Маскируем модуль под OExtension.name, чтобы работали импорты внутри архива
            module.__name__ = fullname
            module.__package__ = fullname.rpartition('.')[0]
            
            sys.modules[fullname] = module
            return module
        
        except Exception as e:
            if fullname in sys.modules:
                del sys.modules[fullname]
            raise OAddonsInit(fullname, e)
