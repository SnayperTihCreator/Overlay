import logging
from core.default_configs import *
from .metadata import MetaDataFinder, registry, MetaData

logger = logging.getLogger(__name__)


@registry
class OverlayDataFinder(MetaDataFinder):
    _conversion_table_ = {"App": ("App", "apps")}
    
    @staticmethod
    def _get_data(type_, name):
        """Reads configuration file content."""
        try:
            path = ""
            match type_:
                case "plugins":
                    path = f"plugin://{name}/plugin.toml"
                case "apps":
                    path = "qt://app/overlay.toml"
                case "theme":
                    path = f"resource://theme/{name}/theme.toml"
            
            if path:
                with open(path, encoding="utf-8") as f:
                    return f.read()
        
        except FileNotFoundError:
            logger.debug(f"Config file not found: {type_}/{name}")
            return None
        except Exception as e:
            logger.error(f"Error reading config for {type_}/{name}: {e}", exc_info=True)
            return None
        
        return None
    
    def find_metadata(self, context: "MetaDataFinder.Context") -> MetaData:
        if not (context.name and context.type):
            return None
        
        logger.debug(f"Finding metadata for: type={context.type}, name={context.name}")
        
        try:
            raw_data = self._get_data(context.type, context.name)
            if not raw_data:
                return None
            
            match context.type:
                case "plugins":
                    return PluginConfig.from_toml(raw_data).metadata
                case "apps":
                    return AppConfig.from_toml(raw_data).metadata
                case "theme":
                    return ThemeConfig.from_toml(raw_data).metadata
        
        except Exception as e:
            logger.warning(f"Failed to parse metadata for {context.type}/{context.name}: {e}")
            return None
        
        return None
