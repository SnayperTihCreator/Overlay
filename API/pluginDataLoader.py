from typing import Any

import yaml

from API.config import Config


def load(path, config: Config):
    with open(f"pldata://{config.name}/{path}", encoding="utf-8") as file:
        return yaml.load(file, yaml.SafeLoader)


def save(path, config: Config, data: Any):
    with open(f"pldata://{config.name}/{path}", "w", encoding="utf-8") as file:
        return yaml.dump(data, file, yaml.SafeDumper)
