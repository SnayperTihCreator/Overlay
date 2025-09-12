from typing import Any

from pydantic import Field

from .metadata import MetaDataFinder, BaseMetaData, registry


class OverlayMetadata(BaseMetaData): ...


class OverlayThemeMetadata(BaseMetaData):
    version: Any = Field("<no version>")


@registry
class OverlayDataFinder(MetaDataFinder):
    _conversion_table_ = {"App": ("App", "apps")}
    
    @staticmethod
    def _get_data(type_, name):
        match type_:
            case "plugins":
                return open(f"plugin://{name}/metadata.toml", encoding="utf-8").read()
            case "apps":
                return open(f"qt://app/metadata.toml", encoding="utf-8").read()
            case "theme":
                return open(f"resource://theme/{name}/theme.toml").read()
    
    def find_metadata(self, context: "MetaDataFinder.Context"):
        if not (bool(context.name) and bool(context.type)): return
        if context.type != "theme":
            return OverlayMetadata.from_toml(self._get_data(context.type, context.name))
        return OverlayThemeMetadata.from_toml(self._get_data(context.type, context.name))
