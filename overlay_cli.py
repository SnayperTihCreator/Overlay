import typer

from APIService.webControls import ClientWebSockets

app = typer.Typer(rich_markup_mode="rich")

@app.command(help="Run action overlay")
def action(port: int, uname: str):
    try:
        socket = ClientWebSockets(port)
        socket.send_message(f"action {uname}")
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


@app.command(name="pass")
def action2(port: int, msg: str):
    try:
        socket = ClientWebSockets(port)
        socket.send_message(f"print {msg}")
    except ConnectionRefusedError:
        typer.secho("У Overlay не запущен websocket", fg=typer.colors.RED)
        raise typer.Exit(code=1225)


if __name__ == '__main__':
    app()
