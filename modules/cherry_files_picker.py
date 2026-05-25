
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button

from utilities.git_functions import get_branches
from widgets.filterable_option_picker import FilterableOptionPicker

class CherryFilesPicker(Vertical):

    def compose(self) -> ComposeResult:
        with Vertical(id="cherry_files_picker"):
            yield Label("Cherry Files Picker", classes="header", variant="success", expand=True)
            with Vertical(classes="branches_selector"):
                with Horizontal():
                    yield FilterableOptionPicker(label="[1] Source Branch", id="source_branch", classes="container")
                    yield FilterableOptionPicker(label="[2] Target Branch", id="target_branch", classes="container")

    def on_mount(self) -> None:
        branches = get_branches()
        if len(branches) == 0:
            self.notify("No branches found. Please make sure to be in a git repo", severity="error")
            return
        self.query_one("#source_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#target_branch", FilterableOptionPicker).set_items(branches)

