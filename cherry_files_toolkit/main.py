from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer
from textual.containers import Horizontal

from cherry_files_toolkit.modules.cherry_files_diff import CherryFilesDiff
from cherry_files_toolkit.modules.cherry_files_picker import CherryFilesPicker


class MyApp(App):
    CSS = """
        CherryFilesDiff {
            width: 40%;
        }

        CherryFilesPicker {
            width: 60%;
        }
    """

    BINDINGS = [
        Binding(key="ctrl+q", action="quit", description="[Ctrl+q]Quit the app")
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Header(icon="🍒")
            yield CherryFilesDiff()
            yield CherryFilesPicker()
            yield Footer(show_command_palette=True)

    def on_mount(self) -> None:
        self.title = "Cherry Files Toolkit"

def run() -> None:
    MyApp().run()

if __name__ == "__main__":
    run()
