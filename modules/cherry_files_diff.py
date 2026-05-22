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
                    yield FilterableOptionPicker(label="Divergent Branch", id="divergent_branch")
                    yield FilterableOptionPicker(label="Base Branch", id="base_branch")
                yield Button("Start Diff Checker", id="start_diff_checker")
            with Vertical(classes="container"):
                yield Label("Summary")
                yield Label(id="summary_label")
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
        changed_files = get_all_changed_files(divergent=divergent, commit_id=commit_id)
        added_files, modified_files, deleted_files = self.parsed_files(changed_files)
        await self.render_files(added_files, modified_files, deleted_files)


    def parsed_files(self, changed_files):
        added_files = []
        modified_files = []
        deleted_files = []

        for line in changed_files:
            parts = line.split("\t")

            if len(parts) < 2:
                continue

            status = parts[0]
            path = parts[-1]

            if status == "A":
                added_files.append(path)
            if status == "M":
                modified_files.append(path)
            if status == "D":
                deleted_files.append(path)
            if status.startswith(("R", "C")):
                modified_files.append(path)

        return added_files, modified_files, deleted_files

    async def render_files(self, added_files, modified_files, deleted_files) -> None:
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        summary_label = self.query_one("#summary_label", Label)
        await files_container.remove_children()

        added_files_counter = len(added_files)
        modified_files_counter = len(modified_files)
        deleted_files_counter = len(deleted_files)
 
        # SUMMARY
        summary_label.update(f"+{added_files_counter} created ~{modified_files_counter} modified -{deleted_files_counter} deleted")

        await self.render_tree_files("ADDED FILES", "green_text", added_files)
        await self.render_tree_files("MODIFIED FILES", "yellow_text", modified_files)
        await self.render_tree_files("DELETED FILES", "red_text", deleted_files)

    async def render_tree_files(self, label:str, label_class:str, files:list[str]) -> None:
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        await files_container.mount(Label(label, classes=label_class))
        await files_container.mount_all(Label(a) for a in files)








