from typing import Optional
import builtins

from pyi18n import PyI18n
from pyi18n.loaders import PyI18nBaseLoader


class CustomPyI18n(PyI18n):
    def __init__(self, available_locales: tuple, load_path: str = 'locales/',
                 loader: Optional[PyI18nBaseLoader] = None) -> None:
        super().__init__(available_locales, load_path, loader)
        builtins.tr = self.gettext


