import os
import zipimport
import re
import sys
import logging

from fs import open_fs
from core.errors import OAddonsNotFound, OAddonsInit

logger = logging.getLogger(__name__)


class OverlayAddonsLoader:
    def __init__(self):
        self.fs = open_fs("resource://overlay_addons", create=True)
        logger.info("OverlayAddonsLoader ready.")
    
    def _find_addon_file(self, addon_name: str) -> str:
        """Searches for .oaddons file in resource folder."""
        try:
            for file in self.fs.listdir(""):
                clean = re.sub(r'(\.oaddons|\[.*?\])', '', file).strip()
                if clean == addon_name:
                    return file
        except Exception as e:
            logger.error(f"Error listing addon files: {e}", exc_info=True)
        return None
    
    def exists(self, addon_name: str) -> bool:
        return self._find_addon_file(addon_name) is not None
    
    def import_module(self, fullname: str):
        addon_name = fullname.split(".")[-1]
        logger.info(f"Loading addon: {addon_name}")
        filename = self._find_addon_file(addon_name)
        
        if not filename:
            logger.warning(f"Addon file not found for: {fullname}")
            raise OAddonsNotFound(fullname)
        
        try:
            zip_path = self.fs.getsyspath(filename)
            if os.name == 'nt' and zip_path.startswith('/'):
                zip_path = zip_path.lstrip('/')
            
            inner_path = os.path.join(zip_path, addon_name).replace("\\", "/")
            
            try:
                importer = zipimport.zipimporter(inner_path)
            except zipimport.ZipImportError:
                importer = zipimport.zipimporter(zip_path + ".oaddons")
            
            module = importer.load_module(os.path.basename(zip_path))
            
            module.__name__ = fullname
            module.__package__ = fullname.rpartition('.')[0]
            
            sys.modules[fullname] = module
            logger.info(f"Addon loaded successfully: {fullname}")
            return module
        
        except Exception as e:
            logger.warning(f"Failed to load addon '{fullname}': {e}")
            logger.error(f"Critical error loading '{fullname}'", exc_info=True)
            if fullname in sys.modules:
                del sys.modules[fullname]
            raise OAddonsInit(fullname, e)
