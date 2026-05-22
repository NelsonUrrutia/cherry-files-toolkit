from textual.app import ComposeResult
from textual import on
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label

from utilities.git_functions import get_branches, get_divergence_point, get_all_changed_files
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
                yield VerticalScroll(id="files_scroll_container")

    def on_mount(self) -> None:
        branches = get_branches()
        if len(branches) == 0:
            self.notify("No branches found. Please make sure to be in a git repo", severity="error")
            return
        self.query_one("#base_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#divergent_branch", FilterableOptionPicker).set_items(branches)

    @on(Button.Pressed, "#start_diff_checker")
    async def start_diff_checker_handler(self) -> None:
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
            return

        await self.files_diff(base_branch, divergent_branch)


    async def files_diff(self, base:str, divergent:str) -> None:
        commit_id = get_divergence_point(base=base, branch=divergent)
        changed_files = get_all_changed_files(base=base, commit_id=commit_id)
        await self.categorized_files(changed_files)

    async def categorized_files(self, changed_files) -> None:
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        await files_container.remove_children()
        await files_container.mount_all(Label(p) for p in changed_files)
