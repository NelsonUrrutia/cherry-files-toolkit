from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Button, Input, Label, SelectionList

from utilities.git_functions import get_branches, get_current_branch, cherry_pick_files
from widgets.filterable_option_picker import FilterableOptionPicker


class CherryFilesPicker(Vertical):
    def compose(self) -> ComposeResult:
        with Vertical(id="cherry_files_picker"):
            yield Label(
                "Cherry Files Picker", classes="header", variant="success", expand=True
            )
            with Vertical(classes="branches_selector"):
                with Horizontal():
                    with Vertical():
                        yield Label("[1] Source Branch")
                        yield Input(id="source_branch", disabled=True)
                    yield FilterableOptionPicker(
                        label="[2] Target Branch",
                        id="target_branch",
                        classes="container",
                    )
            with Vertical(id="cherry_files_tree_container", classes="container"):
                with Vertical(id="files_panel"):
                    yield Label("[3] Files", classes="section_label")
                    yield Input(
                        placeholder="Type to search files", id="search_files_input"
                    )
                    yield SelectionList(id="files_scroll_container")
            with Vertical(classes="container"):
                yield Label("[4] Commit", classes="section_label")
                with Vertical(classes="commit_section_item"):
                    yield Label("Commit title")
                    yield Input(id="commit_title")
                with Vertical(classes="commit_section_item"):
                    yield Label("Commit description")
                    yield Input(id="commit_description")
                with Vertical(classes="commit_section_item"):
                    yield Label("Selected files")
                    yield VerticalScroll(id="selected_files_container")
                yield Button(
                    label="Cherry Pick Files",
                    id="cta_cherry_pick_files",
                    variant="success",
                    compact=True,
                    flat=True,
                )

    def on_mount(self) -> None:
        branches = get_branches()
        if len(branches) == 0:
            self.notify(
                "No branches found. Please make sure to be in a git repo",
                severity="error",
            )
            return
        self.query_one("#target_branch", FilterableOptionPicker).set_items(branches)
        current_branch = get_current_branch()
        if current_branch:
            self.query_one("#source_branch", Input).value = current_branch
        self.selected_files = []
        self.all_files = self.get_all_project_files()
        self.render_file_options(self.all_files)

    @on(Input.Changed, "#search_files_input")
    def filter(self, event: Input.Changed):
        text = event.value.strip().lower()
        if len(text) < 4:
            self.render_file_options(self.all_files)
            return

        filtered_files = [x for x in self.all_files if text in x.lower()]
        self.render_file_options(filtered_files)

    @on(SelectionList.SelectedChanged, "#files_scroll_container")
    async def files_selected_changed(
        self, event: SelectionList.SelectedChanged[str]
    ) -> None:
        currently_selected = set(event.selection_list.selected)
        visible = getattr(self, "_visible_files", set())
        updated = [f for f in self.selected_files if f not in visible]
        updated.extend(currently_selected)
        self.selected_files = updated
        await self.render_selected_files_list()

    @on(Button.Pressed, "#cta_cherry_pick_files")
    def cta_cherry_pick_files_handler(self) -> None:
        target_branch = self.query_one("#target_branch", FilterableOptionPicker).get_search_value()
        source_branch = self.query_one("#source_branch", Input).value
        selected_files = self.selected_files
        commit_title = self.query_one("#commit_title", Input).value
        commit_description = self.query_one("#commit_description", Input).value

        if target_branch.strip() == "":
            self.notify("Please select a Target Branch", severity="warning")
            return
        if len(selected_files) == 0:
            self.notify("Please select at least one file", severity="warning")
            return
        
        success, message = cherry_pick_files(source_branch, target_branch, selected_files, commit_title, commit_description)
        if success:
            self.notify(message, severity="information")
        else:
            self.notify(message, severity="information")

    async def render_selected_files_list(self):
        list_container = self.query_one("#selected_files_container", VerticalScroll)
        await list_container.remove_children()
        for item in self.selected_files:
            await list_container.mount(Label(item))

    def render_file_options(self, filtered_files):
        selection_list = self.query_one("#files_scroll_container", SelectionList)
        self._visible_files = set(filtered_files)
        selection_list.clear_options()
        selection_list.add_options(
            (file_path, file_path, file_path in self.selected_files)
            for file_path in filtered_files
        )

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
