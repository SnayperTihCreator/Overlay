import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
import logging

from .generator import generate_stub

# Инициализируем консоль Rich для красивого вывода
console = Console()
app = typer.Typer(
    name="stubgen",
    help="Генератор .pyi файлов для Overlay API",
    add_completion=False,
)


def setup_logging(verbose: bool):
    """Настройка красивого логгирования через Rich."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )


@app.command()
def generate(
        source: Path = typer.Argument(
            ...,
            help="Путь к исходному файлу (например, src/oapi.py)",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
        output: Path = typer.Option(
            Path("oapi.pyi"),
            "--output", "-o",
            help="Путь для сохранения результата",
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose", "-v",
            help="Показывать подробные логи анализа",
        ),
):
    """
    Генерирует типизированную заглушку (.pyi) на основе анализа AST.
    """
    setup_logging(verbose)
    
    with console.status(f"[bold green]Анализируем {source.name}...", spinner="dots"):
        try:
            content = generate_stub(str(source))
            
            output.write_text(content, encoding="utf-8")
            
            console.print(f"\n[bold green]✔[/bold green] Файл успешно сохранен: [bold cyan]{output}[/bold cyan]")
        
        except Exception as e:
            console.print(f"\n[bold red]✘ Ошибка при генерации:[/bold red] {e}")
            if verbose:
                logging.exception("Детали ошибки:")
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app(help_option_names=["--help", "-h"])