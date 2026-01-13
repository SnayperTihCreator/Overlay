import re
import zipfile
from pathlib import Path

from toml import dumps

from .core import setup_type, BaseProject

__all__ = ["PluginProject", "ThemeProject", "OAddonsProject", "PackProject"]


@setup_type("plugin")
class PluginProject(BaseProject):
    def _pack(self, dist_path: Path):
        resultFile = dist_path / "compress" / f"{self.name}.plugin"
        resultFile.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"packing {resultFile.as_posix()}")
        
        with zipfile.ZipFile(resultFile, "w") as zfile:
            zfile.mkdir(self.name)
            for entry in self._filtered_rglob():
                arcname = entry.relative_to(self.root)
                self.logger.info(f"copy {entry.as_posix()} as {arcname.as_posix()}")
                
                if entry.is_dir():
                    continue
                if entry.suffix == ".py":
                    self.logger.info(f"packing module {arcname.as_posix()} as {self.name}/{arcname.as_posix()}")
                    zfile.write(entry, f"{self.name}/{arcname.as_posix()}")
                else:
                    self.logger.info(f"packing data to {arcname.as_posix()}")
                    if self._match_config(entry):
                        self.add_metadata(entry)
                    zfile.write(entry, arcname)
        self.logger.info("build success")
        return resultFile
    
    def _match_config(self, path: Path) -> bool:
        return path.name == "plugin.toml"


@setup_type("theme")
class ThemeProject(BaseProject):
    def _pack(self, dist_path: Path):
        resultFile = dist_path / "compress" / f"{self.name}.overtheme"
        resultFile.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(resultFile, "w") as zfile:
            for entry in self.root.rglob("*"):
                arcname = entry.relative_to(self.root)
                if entry.is_file() and not self._exclude_file(arcname):
                    if self._match_config(entry):
                        self.add_metadata(entry)
                    zfile.write(entry, arcname)
                elif entry.is_dir() and not self._exclude_folder(arcname):
                    zfile.mkdir(arcname)
        return resultFile
    
    def _match_config(self, path: Path) -> bool:
        return path.name == "theme.toml"


@setup_type("oaddons")
class OAddonsProject(BaseProject):
    def _get_transformed_name(self) -> str:
        name = self.name.replace(" ", "_")
        parts = re.split(r'(\[.*?\]|\(.*?\))', name)
        
        transformed = ""
        for part in parts:
            if part.startswith(('[', '(')):
                transformed += part
            else:
                transformed += part.lower()
        return transformed
    
    def _pack(self, dist_path: Path):
        t_name = self._get_transformed_name()
        resultFile = dist_path / "compress" / f"{t_name}.oaddons"
        resultFile.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(resultFile, "w") as zfile:
            zfile.mkdir(t_name)
            for entry in self.root.rglob("*"):
                arcname = entry.relative_to(self.root)
                if entry.is_dir() and self._exclude_file(arcname):
                    continue
                elif entry.is_file() and self._exclude_folder(arcname):
                    continue
                
                if entry.suffix == ".py":
                    zfile.write(entry, f"{t_name}/{arcname}")
                else:
                    if self._match_config(entry):
                        self.add_metadata(entry)
                    zfile.write(entry, arcname)
        
        return resultFile
    
    def _match_config(self, path: Path) -> bool:
        return path.name == "oaddons.toml"


@setup_type("pack")
class PackProject(BaseProject):
    def _pack(self, dist_path: Path):
        if not (pluginFile := self.options.pop("plugin", False)):
            compress = PluginProject(self.name, self.version, self.root, **self.options)
            pluginFile = compress.build(dist_path)
        
        resultFile = dist_path / "pack" / f"{self.name}.pack"
        resultFile.parent.mkdir(parents=True, exist_ok=True)
        
        toolsFolder = dist_path / "tools"
        tWinFolder = toolsFolder / f"windows-{self.name}"
        tLinuxFolder = toolsFolder / f"linux-{self.name}"
        
        with zipfile.ZipFile(resultFile, "w") as zfile:
            zfile.write(pluginFile, pluginFile.name)
            zfile.mkdir("tools")
            zfile.mkdir("tools/windows")
            zfile.mkdir("tools/linux")
            
            module_win = []
            module_linux = []
            
            if tWinFolder.exists():
                for entry in tWinFolder.rglob("*"):
                    arcname = f"tools/windows/{entry.relative_to(tWinFolder)}"
                    if entry.is_file():
                        zfile.write(entry, arcname)
                    elif entry.is_dir():
                        zfile.mkdir(arcname)
                for entry in tWinFolder.iterdir():
                    if entry.is_dir() and (entry / "__init__.py").exists():
                        module_win.append(entry.name)
            
            if tLinuxFolder.exists():
                for entry in tLinuxFolder.rglob("*"):
                    arcname = f"tools/linux/{entry.relative_to(tLinuxFolder)}"
                    if entry.is_file():
                        zfile.write(entry, arcname)
                    elif entry.is_dir():
                        zfile.mkdir(arcname)
                
                for entry in tLinuxFolder.iterdir():
                    if entry.is_dir() and (entry / "__init__.py").exists():
                        module_linux.append(entry.name)
            
            metadata = {
                "plugin": {
                    "name": self.name,
                    "version": self.version,
                    "author": self.author,
                    "description": self.description,
                    "platforms": self.options.get("platforms", []),
                },
                "tools": {
                    "win32": module_win,
                    "linux": module_linux
                }
            }
            
            zfile.writestr("plugin.toml", dumps(metadata))
        return resultFile
    
    def _match_config(self, path: Path) -> bool:
        return path.name == "plugin.toml"
    