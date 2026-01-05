import os
import sys
from functools import cache
from pathlib import Path
import json5

import typer
import click
from rich.console import Console

import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from core.network import ClientWebSockets

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@cache
def getAppPath():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(os.getcwd())
    )


os.chdir(getAppPath())
settings_file = (getAppPath() / "settings.json5")

if settings_file.exists():
    data = json5.load(open(settings_file, encoding="utf-8"))
else:
    data = {"port": 8000, "ip": "127.0.0.1"}
    with open(settings_file, "w", encoding="utf-8") as file:
        json5.dump(data, file, ensure_ascii=False, indent=4)


@app.command(help="Run action overlay")
def action(uname: str):
    try:
        socket = ClientWebSockets(data["ip"], data["port"])
        result = socket.send_message(f"action {uname}")
        console.print(result.strip())
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


cli = typer.Typer()
app.add_typer(cli, name="cli", help="CLI интерфейсы")


@cli.command(name="call", help="Вызвать CLI интерфейс")
def action_cli_call(interface: str, args: list[str] = typer.Argument(None, click_type=click.ParamType())):
    args = args or []
    try:
        socket = ClientWebSockets(data["ip"], data["port"])
        result = socket.send_message(f"cli {interface} {' '.join(map(str, args))}")
        console.print(result.strip())
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


@cli.command(name="interface", help="Получить список доступных интерфейсов")
def action_cli_interface():
    try:
        socket = ClientWebSockets(data["ip"], data["port"])
        result = socket.send_message(f"cli overlay_cli")
        console.print(result.strip())
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


if __name__ == '__main__':
    app(help_option_names=["--help", "-h"])
