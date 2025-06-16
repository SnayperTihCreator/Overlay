import yaml
from pathlib import Path


def prePath(path, folders):
    if "plugin:/" in path:
        path = path.replace("plugin:/", "", 1)
        return Path(folders["plugin"]) / path


def load(path, folders):
    path = prePath(path, folders)
    with open(path, encoding="utf-8") as file:
        return yaml.full_load(file)
