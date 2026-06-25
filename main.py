from textual.app import App, ComposeResult
from textual.widgets import Header
from textual.containers import Horizontal

from modules.cherry_files_diff import CherryFilesDiff
from modules.cherry_files_picker import CherryFilesPicker


class MyApp(App):
    # CSS_PATH = "my_app.tcss"
    CSS = """
        CherryFilesDiff {
            width: 40%;
        }

        CherryFilesPicker {
            width: 60%;
        }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Header(icon="🍒")
            yield CherryFilesDiff()
            yield CherryFilesPicker()

    def on_mount(self) -> None:
        self.title = "Cherry Files Toolkit"


if __name__ == "__main__":
    app = MyApp()
    app.run()
