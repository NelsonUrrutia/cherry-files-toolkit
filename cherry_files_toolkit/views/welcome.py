from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Label

# Block-text rendering of assets/banner.svg (one char per 10x20 px cell)
LOGO = """\
 ██████ ██   ██ ███████ ██████  ██████  ██    ██     ███████ ██ ██      ███████ ███████     ████████  ██████   ██████  ██      ██   ██ ██ ████████
██      ██   ██ ██      ██   ██ ██   ██  ██  ██      ██      ██ ██      ██      ██             ██    ██    ██ ██    ██ ██      ██  ██  ██    ██
██      ███████ █████   ██████  ██████    ████       █████   ██ ██      █████   ███████        ██    ██    ██ ██    ██ ██      █████   ██    ██
██      ██   ██ ██      ██   ██ ██   ██    ██        ██      ██ ██      ██           ██        ██    ██    ██ ██    ██ ██      ██  ██  ██    ██
 ██████ ██   ██ ███████ ██   ██ ██   ██    ██        ██      ██ ███████ ███████ ███████        ██     ██████   ██████  ███████ ██   ██ ██    ██\
"""

AUTO_DISMISS = 2.5


class WelcomeScreen(Screen[None]):

    DEFAULT_CSS = """
    .welcome_screen{
        height: 1fr;
        align: center middle;
    }
    .welcome_card{
        width: auto;
        max-width: 100%;
        height: auto;
        padding: 1 2;
    }
    .welcome_card Label{
        width: auto;
    }
    .welcome_logo{
        color: #d2042d;
        text-style: bold;
    }
    .welcome_card .welcome_hint{
        width: 100%;
        text-align: center;
        margin-top: 1;
        color: $accent;
        text-style: italic;
    }
    .welcome_card .welcome_phrase{
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(classes="welcome_screen"), Vertical(classes="welcome_card"):
            with Center():
                yield Label(LOGO, classes="welcome_logo", markup=False)
            yield Label("Cherry-pick files, not commits.", classes="welcome_phrase")
            yield Label("press any key to skip", classes="welcome_hint")

    def on_mount(self) -> None:
        self.set_timer(AUTO_DISMISS, self.close)

    def on_key(self, _: Key) -> None:
        self.close()

    def close(self) -> None:
        # returns None on purpose: awaiting dismiss() from a handler is an error
        if self.app.screen is self:
            self.dismiss()
