from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane

from cherry_files_toolkit.modules.cherry_files_diff import CherryFilesDiff
from cherry_files_toolkit.modules.cherry_files_picker import CherryFilesPicker


class MyApp(App):
    BINDINGS = [
        ("ctrl+1", "show_tab('cherry_files_diff')", "Cherry Files Diff"),
        ("ctrl+2", "show_tab('cherry_files_picker')", "Cherry Files Picker"),
        ("ctrl+q", "quit", "[Ctrl+q]Quit the app"),
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

    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab


def run() -> None:
    MyApp().run()


if __name__ == "__main__":
    run()
