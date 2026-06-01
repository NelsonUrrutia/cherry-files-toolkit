from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import  Input, Label, SelectionList

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
            with Vertical(id="cherry_files_tree_container", classes="container"):
                with Vertical(id="files_panel"):
                    yield Label("[3] Files", classes="section_label")
                    yield Input(placeholder="Type to search files", id="search_files_input")
                    yield SelectionList(id="files_scroll_container")
    def on_mount(self) -> None:
        branches = get_branches()
        if len(branches) == 0:
            self.notify("No branches found. Please make sure to be in a git repo", severity="error")
            return
        self.query_one("#source_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#target_branch", FilterableOptionPicker).set_items(branches)
        self.selected_files = []
        self.all_files =  self.get_all_project_files()
        self.render_file_options(self.all_files)

    @on(Input.Changed, "#search_files_input")
    def filter(self, event:Input.Changed):
        text = event.value.strip().lower()
        if len(text) < 4:
            self.render_file_options(self.all_files)
            return

        filtered_files = [x for x in self.all_files if text in x.lower()]
        self.render_file_options(filtered_files)

    @on (SelectionList.SelectedChanged, "#files_scroll_container")
    def files_selected_changed(self, event:SelectionList.SelectedChanged[str]) -> None:
        selected_files = event.selection_list.selected;
        self.selected_files = selected_files

    def render_file_options(self, filtered_files):
        selection_list = self.query_one("#files_scroll_container", SelectionList)
        selection_list.clear_options()
        selection_list.add_options((file_path, file_path, True if file_path in self.selected_files else False) for file_path in filtered_files)

    def get_all_project_files(self) -> list[str]:
        root_path = Path(".")
        files: list[str] = []
        skipped_directories = {".git", ".venv", "node_modules", "__pycache__"}
        for path in root_path.rglob("*"):
            if any(part in skipped_directories for part in path.parts):
                continue
            if path.is_file():
                files.append(path.relative_to(root_path).as_posix())
        return files
