from pathlib import Path, PurePath
from textual.app import App, ComposeResult
from textual.widgets import MarkdownViewer, Header, Footer, DirectoryTree, Markdown
from textual.containers import Container
from textual.binding import Binding
from textual.logging import TextualHandler
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.WARNING,
    handlers=[logging.FileHandler("debug.log")],
)


class CustomMarkdownViewer(MarkdownViewer):
    # async def _on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
    #
    #     if message.href.startswith("https://") or message.href.startswith("http://"):
    #         message.stop()
    #         self.app.open_url(message.href)
    #     else:
    #         await super()._on_markdown_link_clicked(message)
    #
    #
    async def go(self, location: str | PurePath) -> None:
        if not(location.startswith("https://") or location.startswith("http://")):
            await super().go(location)
        else:
            self.app.open_url(location)
    pass


class MarkdownViewerApp(App):
    CSS = """
    #app-container {
        layout: horizontal;
        height: 100%;
    }
    #file-tree {
        width: 30%;
        height: 100%;
        display: none;
        dock: left;
    }
    #viewer-container {
        width: 100%;
        height: 100%;
        overflow: auto;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Выход"),
        Binding("f", "toggle_files", "Файлы"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-container"):
            yield DirectoryTree("./", id="file-tree")
            with Container(id="viewer-container"):
                yield CustomMarkdownViewer(id="md-viewer", open_links=False)
        yield Footer()
    
    def on_mount(self) -> None:
        self.query_one("#file-tree").display = False
        # Загрузка начального файла
        initial_file = Path("README.md")
        if initial_file.exists():
            self.query_one(CustomMarkdownViewer).go(initial_file)
    
    def action_toggle_files(self) -> None:
        tree = self.query_one("#file-tree")
        tree.display = not tree.display
        self.query_one("#viewer-container").styles.width = "auto" if tree.display else "100%"
    
    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        if event.path.suffix.lower() == ".md":
            try:
                await self.query_one(CustomMarkdownViewer).go(event.path)
                self.query_one("#file-tree").display = False
                self.query_one("#viewer-container").styles.width = "100%"
            except Exception as e:
                self.notify(f"Ошибка загрузки файла: {e}", severity="error")


if __name__ == "__main__":
    import sys
    
    app = MarkdownViewerApp()
    
    # Если передан аргумент командной строки - используем его как начальный файл
    if len(sys.argv) > 1:
        initial_file = Path(sys.argv[1])
        if initial_file.exists():
            async def set_initial_file():
                await app.query_one(CustomMarkdownViewer).go(initial_file)
    else:
        async def set_initial_file():
            await app.query_one(CustomMarkdownViewer).go("README.md")
    
    app.call_later(set_initial_file)
    app.run()