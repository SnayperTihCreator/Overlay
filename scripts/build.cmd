cd /d "%~dp0.."
uv sync
uv run pyinstaller scripts/overlay.spec --noconfirm