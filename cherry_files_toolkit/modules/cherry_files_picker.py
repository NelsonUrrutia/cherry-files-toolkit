from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Button, Input, Label, SelectionList

from cherry_files_toolkit.utilities.git_functions import get_branches, get_current_branch, cherry_pick_files
from cherry_files_toolkit.widgets.filterable_option_picker import FilterableOptionPicker


class CherryFilesPicker(Vertical):
    DEFAULT_CSS = """
        /* Fills the screen and never scrolls itself: one child (#body)
           is 1fr and absorbs all the leftover height. */
        #cherry_files_picker {
            height: 1fr;
        }

        /* Top chrome: as tall as its content. The row and its columns must
           be auto, otherwise the containers default to height: 1fr and eat
           the whole panel, pushing #body off-screen. */
        .branches_selector {
            height: auto;
        }

        #branch_row {
            height: auto;
        }

        #source_branch_col {
            height: auto;
            width: 1fr;
        }

        #target_branch {
            width: 1fr;
        }

        /* Numbered section headings are bold. */
        .section_label,
        #target_branch Label {
            text-style: bold;
        }

        /* The flexible body: two columns sharing all remaining height. */
        #body {
            height: 1fr;
        }

        /* Left column flexes to fill width; its list absorbs the column
           height and scrolls internally instead of growing to every row. */
        #files_panel {
            width: 1fr;
            height: 1fr;
        }

        #files_scroll_container {
            height: 1fr;
        }

        /* Right column: fixed-width commit form. */
        #commit_container {
            width: 50;
            height: 1fr;
            margin-left: 1;
        }

        /* Form fields size to content; the selected-files list soaks up
           whatever height is left in the column and scrolls internally. */
        .commit_section_item {
            height: auto;
        }

        #selected_files_item {
            height: 1fr;
        }

        #selected_files_container {
            height: 1fr;
            border: solid white;
        }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="cherry_files_picker"):
            with Vertical(classes="branches_selector"):
                with Horizontal(id="branch_row"):
                    with Vertical(id="source_branch_col"):
                        yield Label("[1] Source Branch", classes="section_label")
                        yield Input(id="source_branch", disabled=True)
                    yield FilterableOptionPicker(
                        label="[2] Target Branch",
                        id="target_branch",
                        classes="container",
                    )
            with Horizontal(id="body"):
                with Vertical(id="files_panel", classes="container"):
                    yield Label("[3] Files", classes="section_label")
                    yield Input(
                        placeholder="Type to search files", id="search_files_input"
                    )
                    yield SelectionList(id="files_scroll_container")
                with Vertical(id="commit_container", classes="container"):
                    yield Label("[4] Commit", classes="section_label")
                    with Vertical(classes="commit_section_item"):
                        yield Label("Commit title")
                        yield Input(id="commit_title")
                    with Vertical(classes="commit_section_item"):
                        yield Label("Commit description")
                        yield Input(id="commit_description")
                    with Vertical(
                        id="selected_files_item", classes="commit_section_item"
                    ):
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
        target_branch = self.query_one(
            "#target_branch", FilterableOptionPicker
        ).get_search_value()
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

        success, message = cherry_pick_files(
            source_branch,
            target_branch,
            selected_files,
            commit_title,
            commit_description,
        )
        if success:
            self.notify(message, severity="information")
            self.reset_form()
        else:
            self.notify(message, severity="error")

    def reset_form(self):
        self.query_one("#target_branch").query_one("#search", Input).value = ""
        self.query_one("#search_files_input", Input).value = ""
        self.query_one("#commit_title", Input).value = ""
        self.query_one("#commit_description", Input).value = ""
        self.selected_files = []
        self.render_file_options(self.all_files)
        self.query_one("#selected_files_container", VerticalScroll).remove_children()

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
