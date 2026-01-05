from core.default_configs import *
from .metadata import MetaDataFinder, registry, MetaData


@registry
class OverlayDataFinder(MetaDataFinder):
    _conversion_table_ = {"App": ("App", "apps")}
    
    @staticmethod
    def _get_data(type_, name):
        match type_:
            case "plugins":
                return open(f"plugin://{name}/plugin.toml", encoding="utf-8").read()
            case "apps":
                return open(f"qt://app/overlay.toml", encoding="utf-8").read()
            case "theme":
                return open(f"resource://theme/{name}/theme.toml").read()
        return None
    
    def find_metadata(self, context: "MetaDataFinder.Context") -> MetaData:
        if not (bool(context.name) and bool(context.type)):
            return
        
        match context.type:
            case "plugins":
                return PluginConfig.from_toml(self._get_data(context.type, context.name)).metadata
            case "apps":
                return AppConfig.from_toml(self._get_data(context.type, context.name)).metadata
            case "theme":
                return ThemeConfig.from_toml(self._get_data(context.type, context.name)).metadata
