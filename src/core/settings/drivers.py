from pathlib import Path
import json

import toml
import yaml
import json5

__all__ = ["BaseDriver", "YamlDriver", "JsonDriver", "TomlDriver", "Json5Driver"]


class BaseDriver:
    def read(self, path: Path) -> dict: raise NotImplementedError
    
    def write(self, path: Path, data: dict): raise NotImplementedError


class YamlDriver(BaseDriver):
    def read(self, path: Path) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def write(self, path: Path, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)


class JsonDriver(BaseDriver):
    def read(self, path: Path) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    
    def write(self, path: Path, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


class Json5Driver(BaseDriver):
    def read(self, path: Path) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json5.load(f) or {}
    
    def write(self, path: Path, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            json5.dump(data, f, indent=4, ensure_ascii=False)


class TomlDriver(BaseDriver):
    def read(self, path: Path) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return toml.load(f) or {}
    
    def write(self, path: Path, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
