import hashlib
import subprocess
import logging
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable, Type
from abc import ABC, abstractmethod

from jinja2 import Environment, PackageLoader
import toml


class BaseProject(ABC):
    env = Environment(loader=PackageLoader("overlay_sdk", "templates"))
    
    logger = logging.getLogger("OverlaySDK")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    
    def __init__(self, name: str, version: str, root: Path, **kwargs):
        self.name = name
        self.version = version
        self.author = kwargs.pop("author", "<unknown>")
        self.description = kwargs.pop("description", "<unknown>")
        self.root = Path(root).absolute()
        self.exclude_files: list[str] = [*kwargs.pop("exclude_files", []), "*.tmp", "*.qrc", "*.hash"]
        self._validated(self.exclude_files, lambda x: "." not in x)
        self.exclude_folders: list[str] = [*kwargs.pop("exclude_folders", []), "__pycache__", "assets", "dist"]
        self._validated(self.exclude_folders, lambda x: "." in x)
        self.options = kwargs
        self.pre_build_hooks: list[Callable] = []
    
    @staticmethod
    def _validated(lst: list, callback: Callable):
        for item in lst:
            if callback(item): raise ValueError("no validate")
    
    @abstractmethod
    def check_integrity(self) -> bool:
        """Проверяет наличие обязательных файлов перед сборкой"""
        pass
    
    @staticmethod
    def _get_hash(path: Path):
        return hashlib.md5(path.read_bytes()).hexdigest() if path.exists() else ""
    
    def _exclude_folder(self, path: Path):
        for exc_folder in self.exclude_folders:
            if exc_folder in path.parts:
                return True
        return False
    
    def _exclude_file(self, path: Path):
        if self._exclude_folder(path.parent):
            return True
        for exc_file in self.exclude_files:
            if fnmatch(path.as_posix(), exc_file):
                return True
        return False
    
    def _filtered_rglob(self):
        for entry in self.root.rglob("*"):
            if entry.is_dir() and self._exclude_folder(entry):
                continue
            if entry.is_file() and self._exclude_file(entry):
                continue
            yield entry
    
    def compile_resource(self):
        self.logger.info("build resource")
        for qrc in self.root.rglob("*.qrc"):
            output = qrc.with_name(f"{qrc.stem}_rc.py")
            hash_path = qrc.with_suffix(".hash")
            current_hash = self._get_hash(qrc)
            
            if hash_path.exists() and hash_path.read_text() == current_hash and output.exists():
                self.logger.info(f"{qrc.name} not change")
                continue  # Пропускаем, если ничего не менялось
            
            self.logger.info(f"build {qrc.name}")
            result = subprocess.run(["uv", "run", "pyside6-rcc", qrc.as_posix(), "-o", output.as_posix()], check=True)
            hash_path.write_text(current_hash)
            if result.returncode:
                self.logger.warning(f"failed build {qrc.name}: {result.stderr}")
            else:
                self.logger.info(f"success build {qrc.name}")
        self.logger.info("ресурсы собраны")
    
    def build(self, dist_path: Path):
        for hook in self.pre_build_hooks:
            try:
                hook(self, dist_path)
            except Exception as e:
                self.logger.warning(f"hook {hook.__name__} run failed: {e}")
            else:
                self.logger.info(f"hook success {hook.__name__}")
        self.compile_resource()
        return self._pack(dist_path)
    
    def add_metadata(self, path: Path):
        with open(path, "r", encoding="utf-8") as file:
            config = toml.load(file)
        config["metadata"] = {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description
        }
        with open(path, "w", encoding="utf-8") as file:
            toml.dump(config, file)
    
    @abstractmethod
    def _pack(self, dist_path: Path):
        ...
    
    @abstractmethod
    def _match_config(self, path: Path) -> bool:
        ...
    
    @classmethod
    def create_setup_file(cls, kind: str, dist: Path, context: dict):
        output_path = dist / "setup.py"
        if output_path.exists():
            cls.logger.warning(f"setup.py already exists in {dist}")
            return
        
        template = cls.env.get_template(f"{kind}/setup.py.j2")
        dist.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template.render(**context), encoding="utf-8")
    
    @classmethod
    def create_data_file(cls, kind: str, dist: Path, context: dict):
        template_path = Path(__file__).parent / "templates" / kind / f"{kind}.toml.j2"
        output_path = dist / template_path.name.removesuffix(".j2")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        template = cls.env.get_template(f"{kind}/{template_path.name}")
        output_path.write_text(template.render(**context), encoding="utf-8")
        cls.logger.info(f"create data file {kind}/{template_path.name}")
    
    @classmethod
    def create_layout(cls, kind: str, dist: Path, context: dict):
        template_dir = Path(__file__).parent / "templates" / kind
        
        for template_file in template_dir.rglob("*.j2"):
            rel_path = template_file.relative_to(template_dir)
            dest_path = dist / rel_path.with_suffix('')
            
            rendered_name = cls.env.from_string(dest_path.name).render(**context)
            
            dest_path = dest_path.with_name(rendered_name)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            template_name = f"{kind}/{rel_path.as_posix()}"
            template = cls.env.get_template(template_name)
            dest_path.write_text(template.render(**context), encoding="utf-8")


PROJECT_REGISTRY: dict[str, Type[BaseProject]] = {}


def setup_type(name: str):
    def decorator(cls):
        PROJECT_REGISTRY[name] = cls
        return cls
    
    return decorator
