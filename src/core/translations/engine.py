import logging
import weakref
from typing import Any

from ldt import NexusStore, NexusField, LDT, MemoryDriver
from .loaders import BaseLoader

logger = logging.getLogger(__name__)


class I18nEngine(NexusStore):
    """
    Reactive Internationalization Engine.
    Data stored in Nexus at 'translations.{lang}'
    """
    
    current_lang = NexusField("i18n.current_lang", default="ru")
    fallback_lang = NexusField("i18n.fallback_lang", default="en")
    
    def __init__(self, config_path: str = "i18n_config.json"):
        super().__init__(config_path, MemoryDriver())
        
        self._loaders: list[BaseLoader] = []
        self._supported_langs: set[str] = {self.current_lang, self.fallback_lang}
        
        self._bound_methods = weakref.WeakKeyDictionary()
        self._widget_registry = weakref.WeakKeyDictionary()
        
        I18nEngine.current_lang.connect(self, self._on_lang_changed)
        
        logger.info("I18nEngine initialized.")
    
    def supported_langs(self) -> set[str]:
        return self._supported_langs.copy()
    
    def add_loader(self, loader: BaseLoader):
        """Adds a translation source and merges data into Nexus"""
        self._loaders.append(loader)
        new_langs = loader.get_available_langs()
        self._supported_langs.update(new_langs)
        
        for lang in new_langs:
            self._ensure_loaded(lang)
        
        self._refresh_all()
        logger.info(f"Translation loader added. Languages: {new_langs}")
    
    def _ensure_loaded(self, lang: str):
        """Lazy loading and merging of data"""
        path = f"translations.{lang}"
        current_data = self.value(path, default={})
        
        with self.blockSignals():
            merged = False
            for loader in self._loaders:
                loader_data = loader.load(lang)
                if loader_data:
                    self._deep_merge(current_data, loader_data)
                    merged = True
            
            if merged:
                self.setValue(path, current_data)
                # logger.debug(f"Loaded translations for: {lang}") # Optional debug
    
    def _deep_merge(self, base: dict, update: dict):
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._deep_merge(base[k], v)
            elif isinstance(base, LDT):
                base.set(k, v)
            else:
                base[k] = v
    
    def tr(self, key: str, **ctx) -> str:
        """Main translation method with logging"""
        res = self.value(f"translations.{self.current_lang}.{key}")
        
        if res is None and self.current_lang != self.fallback_lang:
            res = self.value(f"translations.{self.fallback_lang}.{key}")
        
        if res is None:
            logger.warning(f"Missing translation key: '{key}'")
            return f"!!{key}!!"
        
        if isinstance(res, dict) and "count" in ctx:
            p_key = self._get_plural_key(ctx["count"], self.current_lang)
            res = res.get(p_key, res.get("other", key))
        
        if isinstance(res, str) and ctx:
            try:
                return res.format(**ctx)
            except Exception as e:
                logger.error(f"Formatting error for key '{key}': {e}", exc_info=True)
        
        return str(res)
    
    @staticmethod
    def _get_plural_key(n: int, lang: str) -> str:
        n = abs(n)
        if lang == "ru":
            if n % 10 == 1 and n % 100 != 11: return "one"
            if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20): return "few"
            return "many"
        return "one" if n == 1 else "other"
    
    def _on_lang_changed(self, new_lang: str):
        """NexusField slot"""
        self._ensure_loaded(new_lang)
        self._refresh_all()
        logger.info(f"Language changed to: {new_lang}")
    
    def set_language(self, lang: str):
        """Simple wrapper to change language"""
        if lang in self._supported_langs:
            self.setValue("i18n.current_lang", lang)
            # The slot _on_lang_changed will be called automatically by NexusField
        else:
            logger.warning(f"Language '{lang}' is not supported.")
    
    def bind(self, widget: Any, key: str, prop: str = "text", **ctx):
        if widget not in self._widget_registry:
            self._widget_registry[widget] = {}
        self._widget_registry[widget][prop] = (key, ctx)
        self._apply(widget, prop, key, ctx)
    
    def bind_self(self, obj: Any, method: str = "retranslate"):
        if hasattr(obj, method):
            self._bound_methods[obj] = method
            getattr(obj, method)()
    
    def _apply(self, widget, prop, key, ctx):
        text = self.tr(key, **ctx)
        setter = getattr(widget, f"set{prop[0].upper()}{prop[1:]}", None)
        if setter: setter(text)
    
    def _refresh_all(self):
        """Mass UI update"""
        with self.blockSignals():
            for w, props in list(self._widget_registry.items()):
                for p, (k, c) in props.items():
                    self._apply(w, p, k, c)
            
            for obj, method in list(self._bound_methods.items()):
                try:
                    getattr(obj, method)()
                except Exception as e:
                    # Logs full traceback if a widget crashes during update
                    logger.error(f"UI refresh error in {obj}.{method}(): {e}", exc_info=True)
