from pathlib import Path
from typing import Optional, Any
import inspect

import typer

from .core import PROJECT_REGISTRY, BaseProject, setup_type
from .project_types import *

__all__ = ["setup", "BaseProject", "setup_type"]

app = typer.Typer()

_setup_data = {}


@app.command(name="build", help="Build a project")
def _builder(dist: Optional[Path] = None):
    kind: str = _setup_data["kind"]
    dist = _setup_data["dist"] or dist
    kwargs: dict[str, Any] = _setup_data["kwargs"]
    
    project_cls = PROJECT_REGISTRY[kind]
    project = project_cls(root=_setup_data["root"], **kwargs)

    # Авто-сборка в папку dist
    dist = dist or Path.cwd()
    dist.mkdir(exist_ok=True)
    result = project.build(dist)
    print(f"Successfully built: {result}")


def setup(kind: str, dist: Optional[Path] = None, **kwargs):
    _setup_data["root"] = Path(inspect.stack()[1].filename).parent
    
    if kind not in PROJECT_REGISTRY:
        print(f"Unknown project type: {kind}")
        return
    
    _setup_data["kind"] = kind
    _setup_data["dist"] = dist
    _setup_data["kwargs"] = kwargs
    
    app(help_option_names=["--help", "-h"])
