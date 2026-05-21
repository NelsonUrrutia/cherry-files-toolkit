from textual.app import ComposeResult
from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label

from utilities.git_functions import get_branches
from widgets.filterable_option_picker import FilterableOptionPicker


class CherryFilesDiff(Vertical):

    CSS_PATH = "../my_app.tcss"

    def compose(self) -> ComposeResult:
        with Vertical(classes="section"):
            yield Label("Cherry Files Diff", variant="primary", expand=True)
            with Vertical():
                with Horizontal():
                    yield FilterableOptionPicker(label="Base Branch", id="base_branch")
                    yield FilterableOptionPicker(label="Divergent Branch", id="divergent_branch")
                yield Button("Start Diff Checker", id="start_diff_checker")
            with Vertical():
                yield Label("Summary")

    def on_mount(self) -> None:
        branches = get_branches()
        if len(branches) == 0:
            self.notify("No branches found. Please make sure to be in a git repo", severity="error")
            return
        self.query_one("#base_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#divergent_branch", FilterableOptionPicker).set_items(branches)

    @on(Button.Pressed, "#start_diff_checker")
    def start_diff_checker_handler(self) -> None:
        base_branch = self.query_one("#base_branch", FilterableOptionPicker).get_search_value()
        divergent_branch = self.query_one("#divergent_branch", FilterableOptionPicker).get_search_value()

        if base_branch.strip() == "":
            self.notify("Please select a Base Branch", title="Cherry Diff Files", severity="warning")
            return

        if divergent_branch.strip() == "":
            self.notify("Please select a Divergent Branch", title="Cherry Diff Files", severity="warning")
            return

        if base_branch.strip() ==  divergent_branch.strip():
            self.notify("Base and Divergent branches must be different", severity="error", title="Cherry Diff Files")

        self.notify(f"{base_branch} || {divergent_branch}")
