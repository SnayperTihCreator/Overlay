import sys
import runpy
import io

import contextlib

from utils import getAppPath


def initer():
    with contextlib.redirect_stdout(io.StringIO()):
        oring_argv = sys.argv
        path_tools = getAppPath() / "tools" / "windows"
        path_post_init = path_tools / "win32" / "scripts" / "pywin32_postinstall.py"
        sys.argv = [
            "pywin32_postinstall.py",
            "-install",
            "-quiet",
            "-silent",
            "-destination",
            str(path_tools),
        ]
        runpy.run_path(
            str(path_post_init),
            run_name="__main__",
        )
        sys.argv = oring_argv
