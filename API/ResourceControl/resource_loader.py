import yaml

from API.config import Config


def load(path, config: Config):
    with open(f"pldata://{config.plugin_name}/{path}", encoding="utf-8") as file:
        return yaml.load(file, yaml.SafeDumper)


def save(path, config: Config, data):
    with open(f"pldata://{config.plugin_name}/{path}", "w", encoding="utf-8") as file:
        return yaml.dump(data, file, yaml.SafeDumper)
