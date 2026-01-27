import logging
import weakref
from typing import Any

from ldt import NexusStore, NexusField, JsonDriver, LDT

from core.logger import handler
from .loaders import BaseLoader

logger = logging.getLogger("I18n.Engine")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class I18nEngine(NexusStore):
    """
    Реактивный движок интернационализации.
    Данные хранятся в дереве Nexus по пути 'translations.{lang}'
    """
    
    current_lang = NexusField("i18n.current_lang", default="ru")
    fallback_lang = NexusField("i18n.fallback_lang", default="en")
    
    def __init__(self, config_path: str = "i18n_config.json"):
        super().__init__(config_path, JsonDriver())
        
        self._loaders: list[BaseLoader] = []
        self._supported_langs: set[str] = {self.current_lang, self.fallback_lang}
        
        self._bound_methods = weakref.WeakKeyDictionary()
        self._widget_registry = weakref.WeakKeyDictionary()
        
        I18nEngine.current_lang.connect(self, self._on_lang_changed)
        
    def supported_langs(self) -> set[str]:
        return self._supported_langs.copy()
    
    def add_loader(self, loader: BaseLoader):
        """Добавляет источник переводов и мержит данные в дерево Nexus"""
        self._loaders.append(loader)
        new_langs = loader.get_available_langs()
        self._supported_langs.update(new_langs)
        
        for lang in new_langs:
            self._ensure_loaded(lang)
        
        self._refresh_all()
    
    def _ensure_loaded(self, lang: str):
        """Ленивая подгрузка и мерж данных в Nexus"""
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
    
    def _deep_merge(self, base: dict, update: dict):
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._deep_merge(base[k], v)
            elif isinstance(base, LDT):
                base.set(k, v)
            else:
                base[k] = v
    
    def tr(self, key: str, **ctx) -> str:
        """Основной метод перевода с Warning-системой"""
        res = self.value(f"translations.{self.current_lang}.{key}")
        
        if res is None and self.current_lang != self.fallback_lang:
            res = self.value(f"translations.{self.fallback_lang}.{key}")
        
        if res is None:
            logger.warning(f"[I18n] Missing translation for key: '{key}'")
            return f"!!{key}!!"
        
        if isinstance(res, dict) and "count" in ctx:
            p_key = self._get_plural_key(ctx["count"], self.current_lang)
            res = res.get(p_key, res.get("other", key))
        
        if isinstance(res, str) and ctx:
            try:
                return res.format(**ctx)
            except Exception as e:
                logger.error(f"Formatting error '{key}': {e}")
        
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
        """Слот NexusField: срабатывает при изменении engine.current_lang"""
        self._ensure_loaded(new_lang)
        self._refresh_all()
    
    def set_language(self, lang: str):
        """Простая обертка для смены языка"""
        if lang in self._supported_langs:
            self.setValue("i18n.current_lang", lang)
            self._refresh_all()
            self._on_lang_changed(lang)
        else:
            logger.warning(f"Language '{lang}' is not supported")
    
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
        """Массовое обновление UI с блокировкой сигналов Nexus для скорости"""
        with self.blockSignals():
            for w, props in list(self._widget_registry.items()):
                for p, (k, c) in props.items():
                    self._apply(w, p, k, c)
            for obj, method in list(self._bound_methods.items()):
                try:
                    getattr(obj, method)()
                except Exception as e:
                    logger.error(f"Retranslate error: {e}")
