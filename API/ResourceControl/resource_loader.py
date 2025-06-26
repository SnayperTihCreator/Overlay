import yaml

from API.config import Config


def load(path, config: Config):
    with config.loadFile(path, data_storage="plugin_data") as file:
        return yaml.load(file, yaml.SafeLoader)


def save(path, config: Config, data):
    with config.loadFile(path, "w", "plugin_data") as file:
        return yaml.dump(data, file, yaml.SafeDumper)
