from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static


def colorize_diff(diff_text: str) -> Text:
    "Colours git diff output line by line, like the terminal does"
    text = Text(no_wrap=True)
    for line in diff_text.splitlines():
        if line.startswith(("diff --git", "index ", "--- ", "+++ ", "new file", "deleted file", "similarity", "rename ")):
            style = "bold"
        elif line.startswith("@@"):
            style = "cyan"
        elif line.startswith("+"):
            style = "green"
        elif line.startswith("-"):
            style = "red"
        else:
            style = ""
        text.append(line + "\n", style=style)
    return text


class FileDiffModal(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    FileDiffModal {
        align: center middle;
    }

    #file_diff_dialog {
        width: 90%;
        height: 90%;
        border: round $primary;
        border-title-align: center;
        border-title-style: bold;
        background: $surface;
        padding: 0 1;
    }

    #file_diff_scroll {
        height: 1fr;
        overflow-x: auto;
    }

    #file_diff_content {
        width: auto;
    }

    #file_diff_empty {
        color: $text-muted;
        text-style: italic;
    }

    #close_file_diff {
        width: auto;
        padding: 0 1;
    }
    """

    def __init__(self, path: str, diff_text: str, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.diff_text = diff_text

    def compose(self) -> ComposeResult:
        dialog = Vertical(id="file_diff_dialog")
        dialog.border_title = self.path
        with dialog:
            # Scrolls both ways, so long lines keep their shape instead of wrapping.
            with VerticalScroll(id="file_diff_scroll"):
                if self.diff_text.strip() == "":
                    yield Static("No textual changes", id="file_diff_empty")
                else:
                    yield Static(colorize_diff(self.diff_text), id="file_diff_content")
            yield Button("CLOSE", id="close_file_diff", flat=True)

    def on_mount(self) -> None:
        self.query_one("#file_diff_scroll").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_file_diff":
            self.dismiss()
