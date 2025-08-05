import platform
import sys

from APIService.path_controls import getAppPath


class ToolsIniter:
    def __init__(self, name="tools"):
        self.tools_name = name

    def load(self):
        (getAppPath() / self.tools_name / "common").mkdir(parents=True, exist_ok=True)
        (getAppPath() / self.tools_name / "windows").mkdir(parents=True, exist_ok=True)
        (getAppPath() / self.tools_name / "linux").mkdir(parents=True, exist_ok=True)
        sys.path.insert(0, str(getAppPath() / self.tools_name / "common"))
        match platform.system():
            case "Windows":
                sys.path.insert(0, str(getAppPath() / self.tools_name / "windows"))
            case "Linux":
                sys.path.insert(0, str(getAppPath() / self.tools_name / "linux"))
