from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, SelectionList

from cherry_files_toolkit.utilities.git_functions import (
    cherry_pick_files,
    get_branch_files,
    get_branches,
    get_current_branch,
)
from cherry_files_toolkit.widgets.filterable_option_picker import FilterableOptionPicker


class CherryFilesPicker(Vertical):
    DEFAULT_CSS = """
        /* Fills the screen and never scrolls itself: two columns share
           the width, each 1fr tall. */
        #cherry_files_picker {
            height: 1fr;
            padding: 0 1;
        }

        /* Left: source branch and files. Right: target branch and the
           commit form. In each column one list is 1fr and absorbs the
           leftover height, scrolling internally. */
        #source_column,
        #target_column {
            width: 1fr;
            height: 1fr;
        }

        #target_column {
            margin-left: 1;
        }

        /* Inputs carry their label as a title centred on the top border. */
        .bordered_input {
            border: round $primary;
            border-title-align: center;
            border-title-color: $primary;
            border-title-style: bold;
        }

        .bordered_input:focus {
            border: round $primary-lighten-2;
        }

        /* Separate the files search from the source branch selector. */
        #search_files_input {
            margin-top: 1;
        }

        #files_scroll_container {
            height: 1fr;
            border: round $primary;
            padding: 0;
        }

        #files_scroll_container:focus {
            border: round $primary-lighten-2;
        }

        /* One bordered box holds both commit fields; the inputs are
           compact (no border of their own) and the box lights up while
           either of them has focus. */
        #commit_form {
            height: auto;
            padding: 1;
            border: round $primary;
            border-title-align: center;
            border-title-color: $primary;
            border-title-style: bold;
        }

        #commit_form:focus-within {
            border: round $primary-lighten-2;
        }

        /* Compact inputs are one row tall; give them three with the text
           centred so they read as proper fields. */
        #commit_title,
        #commit_description {
            height: 3;
            padding: 1;
        }

        #commit_description {
            margin-top: 1;
        }

        /* The selected-files list takes whatever height the rest of the
           column leaves (never under 3 rows) and scrolls internally. */
        #selected_files_container {
            height: 1fr;
            min-height: 5;
            border: round $primary;
            border-title-align: center;
            border-title-color: $primary;
            border-title-style: bold;
        }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="cherry_files_picker"):
            with Vertical(id="source_column"):
                yield FilterableOptionPicker(
                    label="[1] Source Branch", id="source_branch"
                )
                search_files = Input(
                    placeholder="Type to search files",
                    id="search_files_input",
                    classes="bordered_input",
                )
                search_files.border_title = "[3] Files"
                yield search_files
                yield SelectionList(id="files_scroll_container")
            with Vertical(id="target_column"):
                yield FilterableOptionPicker(
                    label="[2] Target Branch", id="target_branch"
                )
                with Vertical(id="commit_form") as commit_form:
                    commit_form.border_title = "[4] Commit"
                    yield Input(placeholder="Title", id="commit_title", compact=True)
                    yield Input(
                        placeholder="Description (optional)",
                        id="commit_description",
                        compact=True,
                    )
                selected_files = VerticalScroll(id="selected_files_container")
                selected_files.border_title = "[5] Selected files"
                yield selected_files
                yield Button(
                    label="Cherry Pick Files",
                    id="cta_cherry_pick_files",
                    variant="success",
                    compact=True,
                    flat=True,
                )

    def on_mount(self) -> None:
        # Set up state first so the handlers work even if we bail out below.
        self.selected_files = []
        self.all_files = []
        self._visible_files = set()
        self.branches = []
        self.loaded_source_branch = ""

        branches = get_branches()
        if len(branches) == 0:
            self.notify(
                "No branches found. Please make sure to be in a git repo",
                severity="error",
            )
            return
        self.query_one("#target_branch", FilterableOptionPicker).set_items(branches)
        self.branches = branches
        self.query_one("#source_branch", FilterableOptionPicker).set_items(branches)
        # Start on the checked-out branch; the change handler loads its files.
        current_branch = get_current_branch()
        if current_branch:
            self.query_one("#source_branch", FilterableOptionPicker).set_search_value(
                current_branch
            )

    @on(Input.Changed, "#source_branch #search")
    def source_branch_changed(self, event: Input.Changed) -> None:
        branch = event.value.strip()
        # Only react once the text is a real branch, not while typing.
        if branch not in self.branches or branch == self.loaded_source_branch:
            return
        self.loaded_source_branch = branch
        self.all_files = get_branch_files(branch)
        # Selections from the previous branch may not exist on this one.
        self.selected_files = []
        self.query_one("#search_files_input", Input).value = ""
        self.render_file_options(self.all_files)
        self.query_one("#selected_files_container", VerticalScroll).remove_children()

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
        updated = [f for f in self.selected_files if f not in self._visible_files]
        updated.extend(currently_selected)
        self.selected_files = updated
        await self.render_selected_files_list()

    @on(Button.Pressed, "#cta_cherry_pick_files")
    def cta_cherry_pick_files_handler(self) -> None:
        target_branch = self.query_one(
            "#target_branch", FilterableOptionPicker
        ).get_search_value()
        source_branch = self.query_one(
            "#source_branch", FilterableOptionPicker
        ).get_search_value()
        selected_files = self.selected_files
        commit_title = self.query_one("#commit_title", Input).value
        commit_description = self.query_one("#commit_description", Input).value

        if source_branch.strip() == "":
            self.notify("Please select a Source Branch", severity="warning")
            return
        if target_branch.strip() == "":
            self.notify("Please select a Target Branch", severity="warning")
            return
        if source_branch.strip() == target_branch.strip():
            self.notify(
                "Source and Target branches must be different", severity="error"
            )
            return
        if len(selected_files) == 0:
            self.notify("Please select at least one file", severity="warning")
            return
        if commit_title.strip() == "":
            self.notify("Please enter a commit title", severity="warning")
            self.query_one("#commit_title", Input).focus()
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
