import typer
import click
from rich.console import Console

from APIService.webControls import ClientWebSockets

app = typer.Typer(rich_markup_mode="rich")
concole = Console()


@app.command(help="Run action overlay")
def action(port: int, uname: str):
    try:
        socket = ClientWebSockets(port)
        result = socket.send_message(f"action {uname}")
        typer.secho(result.strip())
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


cli = typer.Typer()
app.add_typer(cli, name="cli")


@cli.command(name="call")
def action_cli_call(port: int, interface: str, args: list[str] = typer.Argument(None, click_type=click.ParamType())):
    args = args or []
    try:
        socket = ClientWebSockets(port)
        result = socket.send_message(f"cli {interface} {' '.join(map(str, args))}")
        typer.secho(result.strip())
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


if __name__ == '__main__':
    app(help_option_names=["--help", "-h"])
