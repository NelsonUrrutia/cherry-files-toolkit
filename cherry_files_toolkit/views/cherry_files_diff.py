from rich.text import Text
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Label

from cherry_files_toolkit.utilities.clipboard import copy_with_system_clipboard
from cherry_files_toolkit.utilities.git_functions import (
    get_all_changed_files,
    get_branches,
    get_divergence_point,
    get_file_diff,
)
from cherry_files_toolkit.views.file_diff_modal import FileDiffModal
from cherry_files_toolkit.widgets.filterable_option_picker import FilterableOptionPicker


class FileLabel(Label):
    "A file row in a tree; clicking it asks to show that file's diff"

    class Selected(Message):
        def __init__(self, path: str) -> None:
            super().__init__()
            self.path = path

    # Styles just the file name, so the tree connectors don't get underlined.
    COMPONENT_CLASSES = {"file-label--name"}

    def __init__(self, connector: str, name: str, path: str, **kwargs):
        super().__init__(connector + name, markup=False, **kwargs)
        self.connector = connector
        self.file_name = name
        self.path = path

    def render(self) -> Text:
        name_style = self.get_component_rich_style("file-label--name")
        return Text.assemble(self.connector, (self.file_name, name_style))

    def on_click(self, event: events.Click) -> None:
        self.post_message(self.Selected(self.path))


class CherryFilesDiff(Vertical):
    # (container id, column title) for each change type, left to right.
    FILE_COLUMNS = (
        ("added_files_container", "Created"),
        ("modified_files_container", "Modified"),
        ("deleted_files_container", "Deleted"),
    )

    DEFAULT_CSS = """
    #cherry_files_diff{
        padding: 0 2;
    }

    /* Top chrome sizes to its content so the summary gets the rest. */
    .branches_selector,
    #branch_row,
    #diff_actions_row {
        height: auto;
    }

    #base_branch,
    #reset_diff_checker {
        margin-left: 1;
    }

    /* Title and counts share one row, right above the columns. */
    #cherry_files_diff_summary_header {
        height: 1;
    }

    #cherry_files_diff_summary_label {
        text-style: bold;
        margin-right: 2;
    }

    /* One scrollable tree per change type, side by side. */
    #files_containers {
        height: 1fr;
    }

    /* Each column stacks its tree above its copy button. */
    .files_column {
        width: 1fr;
        height: 1fr;
    }

    .files_scroll_container {
        height: 1fr;
        border: round $primary;
        border-title-align: center;
        border-title-style: bold;
    }

    .files_scroll_container:focus {
        border: round $primary-lighten-2;
    }

    .no_files {
        color: $text-muted;
        text-style: italic;
    }

    #added_files_container {
        border-title-color: green;
    }

    #modified_files_container {
        border-title-color: orange;
    }

    #deleted_files_container {
        border-title-color: red;
    }

    /* File rows open a diff preview, so make them read like links. */
    FileLabel {
        pointer: pointer;
    }

    FileLabel > .file-label--name {
        text-style: bold;
    }

    FileLabel:hover {
        background: $boost;
    }

    FileLabel:hover > .file-label--name {
        color: $accent;
        text-style: bold underline;
    }

    .files_scroll_container {
        border-subtitle-color: $text-muted;
        border-subtitle-style: italic;
    }

    .copy_tree_button {
        width: auto;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="cherry_files_diff"):
            with Vertical(classes="branches_selector"):
                with Horizontal(id="branch_row"):
                    yield FilterableOptionPicker(
                        label="[1] Divergent Branch",
                        id="divergent_branch",
                        classes="container",
                    )
                    yield FilterableOptionPicker(
                        label="[2] Base Branch", id="base_branch", classes="container"
                    )
                with Horizontal(id="diff_actions_row"):
                    yield Button(
                        "Start Diff Checker",
                        id="start_diff_checker",
                        variant="primary",
                        flat=True,
                    )
                    yield Button("RESET", id="reset_diff_checker", flat=True)
            with Vertical(id="cherry_files_diff_summary"):
                with Horizontal(id="cherry_files_diff_summary_header"):
                    yield Label("[3] Summary", id="cherry_files_diff_summary_label")
                    yield Label(id="cherry_files_diff_summary_counter")
                with Horizontal(id="files_containers"):
                    for container_id, title in self.FILE_COLUMNS:
                        with Vertical(classes="files_column"):
                            files_container = VerticalScroll(
                                id=container_id, classes="files_scroll_container"
                            )
                            files_container.border_title = title
                            yield files_container
                            yield Button(
                                f"COPY {title.upper()} TREE",
                                id=f"copy_{container_id}",
                                name=container_id,
                                classes="copy_tree_button",
                                flat=True,
                                disabled=True,
                            )

    def on_mount(self) -> None:
        # Plain-text tree per container, kept so the copy buttons can grab it.
        self.tree_texts: dict[str, str] = {}
        # (divergent branch, divergence commit) of the last diff, for file diffs.
        self.diff_range: tuple[str, str] | None = None
        branches = get_branches()
        if len(branches) == 0:
            self.notify(
                "No branches found. Please make sure to be in a git repo",
                severity="error",
            )
            return
        self.query_one("#base_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#divergent_branch", FilterableOptionPicker).set_items(branches)

    @on(Button.Pressed, "#start_diff_checker")
    async def start_diff_checker_handler(self) -> None:
        base_branch = self.query_one(
            "#base_branch", FilterableOptionPicker
        ).get_search_value()
        divergent_branch = self.query_one(
            "#divergent_branch", FilterableOptionPicker
        ).get_search_value()

        if base_branch.strip() == "":
            self.notify(
                "Please select a Base Branch",
                title="Cherry Diff Files",
                severity="warning",
            )
            return

        if divergent_branch.strip() == "":
            self.notify(
                "Please select a Divergent Branch",
                title="Cherry Diff Files",
                severity="warning",
            )
            return

        if base_branch.strip() == divergent_branch.strip():
            self.notify(
                "Base and Divergent branches must be different",
                severity="error",
                title="Cherry Diff Files",
            )
            return

        await self.files_diff(base_branch, divergent_branch)

    @on(Button.Pressed, ".copy_tree_button")
    def copy_tree_handler(self, event: Button.Pressed) -> None:
        tree_text = self.tree_texts.get(event.button.name or "", "")
        if tree_text == "":
            return
        # OSC 52 isn't supported by every terminal (e.g. macOS Terminal.app),
        # so prefer the OS clipboard and fall back to Textual's.
        if not copy_with_system_clipboard(tree_text):
            self.app.copy_to_clipboard(tree_text)
        self.notify("Tree copied to clipboard", title="Cherry Diff Files")

    @on(Button.Pressed, "#reset_diff_checker")
    async def reset_diff_checker_handler(self) -> None:
        self.diff_range = None
        for picker in self.query(FilterableOptionPicker):
            picker.reset()
        self.query_one("#cherry_files_diff_summary_counter", Label).update("")
        for container_id, title in self.FILE_COLUMNS:
            files_container = self.query_one(f"#{container_id}", VerticalScroll)
            files_container.border_title = title
            files_container.border_subtitle = ""
            await files_container.remove_children()
            self.tree_texts[container_id] = ""
            self.query_one(f"#copy_{container_id}", Button).disabled = True

    @on(FileLabel.Selected)
    def show_file_diff_handler(self, event: FileLabel.Selected) -> None:
        if self.diff_range is None:
            return
        divergent, commit_id = self.diff_range
        diff_text = get_file_diff(divergent=divergent, commit_id=commit_id, path=event.path)
        self.app.push_screen(FileDiffModal(event.path, diff_text))

    async def files_diff(self, base: str, divergent: str) -> None:
        commit_id = get_divergence_point(base=base, branch=divergent)
        self.diff_range = (divergent, commit_id)
        changed_files = get_all_changed_files(divergent=divergent, commit_id=commit_id)
        added_files, modified_files, deleted_files = self.parsed_files(changed_files)
        await self.render_files(added_files, modified_files, deleted_files)

    async def render_files(self, added_files, modified_files, deleted_files) -> None:
        cherry_files_diff_summary_counter = self.query_one(
            "#cherry_files_diff_summary_counter", Label
        )

        added_files_counter = len(added_files)
        modified_files_counter = len(modified_files)
        deleted_files_counter = len(deleted_files)

        # SUMMARY
        cherry_files_diff_summary_counter.update(
            f"Total: {added_files_counter + modified_files_counter + deleted_files_counter} files touched"
        )

        # Render trees, with each count in its column's border title
        await self.render_tree_files(
            "#added_files_container", f"+{added_files_counter} Created", added_files
        )
        await self.render_tree_files(
            "#modified_files_container",
            f"~{modified_files_counter} Modified",
            modified_files,
        )
        await self.render_tree_files(
            "#deleted_files_container", f"-{deleted_files_counter} Deleted", deleted_files
        )

    async def render_tree_files(
        self, container_id: str, title: str, files: list[str]
    ) -> None:
        files_container = self.query_one(container_id, VerticalScroll)
        files_container.border_title = title
        copy_button = self.query_one(f"#copy_{container_id[1:]}", Button)
        await files_container.remove_children()
        if len(files) == 0:
            self.tree_texts[container_id[1:]] = ""
            copy_button.disabled = True
            files_container.border_subtitle = ""
            await files_container.mount(Label("No files", classes="no_files"))
            return
        await files_container.mount(Label("📂 root", classes="parent_directory"))
        tree = self.build_tree(files)
        lines = ["📂 root"]
        await self.render_tree(files_container, tree, lines)
        self.tree_texts[container_id[1:]] = "\n".join(lines)
        copy_button.disabled = False
        files_container.border_subtitle = "click a file to preview"

    async def render_tree(
        self,
        files_container: VerticalScroll,
        tree,
        lines: list[str],
        prefix="",
        path_prefix="",
    ):
        entries = list(tree.items())
        for i, (name, subtree) in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            if subtree:
                connector += "📂 "
            classes = "parent_directory" if subtree else ""
            lines.append(prefix + connector + name)
            if subtree:
                row = Label(prefix + connector + name, classes=classes)
            else:
                row = FileLabel(prefix + connector, name, path=path_prefix + name)
            await files_container.mount(row)
            self.log(prefix + connector + name)
            if subtree:
                extension = "    " if is_last else "│   "
                await self.render_tree(
                    files_container,
                    subtree,
                    lines,
                    prefix + extension,
                    path_prefix + name + "/",
                )

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

    def build_tree(self, files: list[str]):
        tree = {}
        for path in files:
            node = tree
            parts = path.split("/")
            for part in parts:
                if part not in node:
                    node[part] = {}
                node = node[part]
        return tree
