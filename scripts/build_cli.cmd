cd /d "%~dp0.."
uv sync
uv run pyinstaller scripts/overlay_cli.spec --noconfirm