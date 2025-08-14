import subprocess
import platform
from pathlib import Path


def open_file_manager(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    system = platform.system()

    if system == "Windows":
        subprocess.Popen(["explorer", path])
    elif system == "Linux":
        subprocess.Popen(["xdg-open", path])
    else:
        raise OSError("Unsupported operating system")
