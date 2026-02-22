import asyncio
import sys
import logging
from typing import Any, Self, Coroutine

from PySide6.QtWidgets import QApplication
from ldt.io_drives.drivers.extra import YamlDriver

from core.translations import I18nEngine, QRCLoader

logger = logging.getLogger(__name__)


class MetaSingletonQt(type(QApplication)):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.debug(f"Creating singleton instance for {cls.__name__}")
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class OverlayApplication(QApplication, metaclass=MetaSingletonQt):
    def __init__(self, *args, **kwargs):
        logger.info("Initializing OverlayApplication...")
        
        try:
            self.i18n = I18nEngine()
            
            self.base_loader = QRCLoader(":/i18n/", YamlDriver())
            self.i18n.add_loader(self.base_loader)
            
            super().__init__(*args, **kwargs)
            
            logger.info("OverlayApplication started successfully.")
        
        except Exception as e:
            logger.critical("CRITICAL: Application failed to initialize!", exc_info=True)
            raise e
    
    @classmethod
    def INSTANCE(cls) -> Self:
        if cls._instance is None:
            cls._instance = OverlayApplication(sys.argv)
        return cls._instance
    
    @classmethod
    def bind_translate(cls, obj: Any, method: str = "retranslate"):
        try:
            cls.INSTANCE().i18n.bind_self(obj, method)
        except Exception as e:
            logger.error(f"Failed to bind translation for {obj}: {e}", exc_info=True)
    
    @classmethod
    def text(cls, key, **context):
        return cls.INSTANCE().i18n.tr(key, **context)
    
    @classmethod
    def atext(cls, key, **context) -> Coroutine[Any, Any, Any]:
        """Async wrapper for text translation"""
        return asyncio.to_thread(cls.text, key, **context)
    
    @classmethod
    def get_current_lang(cls):
        return cls.INSTANCE().i18n.current_lang
    
    @classmethod
    def set_language(cls, lang_code: str):
        cls.INSTANCE().i18n.set_language(lang_code)
    
    @classmethod
    def supported_langs(cls):
        return cls.INSTANCE().i18n.supported_langs()