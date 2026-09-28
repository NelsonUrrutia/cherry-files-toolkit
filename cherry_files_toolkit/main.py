from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, TabbedContent, TabPane

from cherry_files_toolkit.views.cherry_files_diff import CherryFilesDiff
from cherry_files_toolkit.views.cherry_files_picker import CherryFilesPicker
from cherry_files_toolkit.views.welcome import WelcomeScreen


class MyApp(App):
    BINDINGS = [
        Binding("ctrl+1", "show_tab('cherry_files_diff')", "Cherry Files Diff", show=False),
        Binding("ctrl+2", "show_tab('cherry_files_picker')", "Cherry Files Picker", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon="🍒")
        yield Footer(show_command_palette=True)

        with TabbedContent(initial="cherry_files_diff"):
            with TabPane("Cherry Files Diff", id="cherry_files_diff"):
                yield CherryFilesDiff()
            with TabPane("Cherry Files Picker", id="cherry_files_picker"):
                yield CherryFilesPicker()

    def on_mount(self) -> None:
        self.title = "Cherry Files Toolkit"
        self.push_screen(WelcomeScreen())

    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab


def run() -> None:
    MyApp().run()


if __name__ == "__main__":
    run()
