from re import sub
from textual.app import ComposeResult
from textual import on
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label

from utilities.git_functions import get_branches, get_divergence_point, get_all_changed_files
from widgets.filterable_option_picker import FilterableOptionPicker


class CherryFilesDiff(Vertical):
    def compose(self) -> ComposeResult:
        with Vertical(id="cherry_files_diff"):
            yield Label("Cherry Files Diff", classes="header", variant="primary", expand=True)
            with Vertical(id="cherry_files_diff_controls"):
                with Horizontal():
                    yield FilterableOptionPicker(label="[1] Divergent Branch", id="divergent_branch", classes="container")
                    yield FilterableOptionPicker(label="[2] Base Branch", id="base_branch", classes="container")
                yield Button("Start Diff Checker", id="start_diff_checker", variant="primary", flat=True)
            with Vertical(id="cherry_files_diff_summary"):
                yield Label("[3] Summary", id="cherry_files_diff_summary_label")
                with Horizontal(id="cherry_files_diff_summary_header"):
                    yield Label(id="cherry_files_diff_summary_added", classes="cherry_files_diff_added_files")
                    yield Label(id="cherry_files_diff_summary_modified", classes="cherry_files_diff_modified_files")
                    yield Label(id="cherry_files_diff_summary_deleted", classes="cherry_files_diff_deleted_files")
                    yield Label(id="cherry_files_diff_summary_counter")
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

    async def render_files(self, added_files, modified_files, deleted_files) -> None:
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        cherry_files_diff_summary_added = self.query_one("#cherry_files_diff_summary_added", Label)
        cherry_files_diff_summary_modified = self.query_one("#cherry_files_diff_summary_modified", Label)
        cherry_files_diff_summary_deleted = self.query_one("#cherry_files_diff_summary_deleted", Label)
        cherry_files_diff_summary_counter = self.query_one("#cherry_files_diff_summary_counter", Label)

        added_files_counter = len(added_files)
        modified_files_counter = len(modified_files)
        deleted_files_counter = len(deleted_files)
 
        # SUMMARY
        cherry_files_diff_summary_added.update(f"+{added_files_counter} created")
        cherry_files_diff_summary_modified.update(f"~{modified_files_counter} modified")
        cherry_files_diff_summary_deleted.update(f"-{deleted_files_counter} delelted")
        cherry_files_diff_summary_counter.update(f"| Total: {added_files_counter + modified_files_counter + deleted_files_counter} files touched")

        # Render trees
        await files_container.remove_children()
        await self.render_tree_files("CREATED FILES", "cherry_files_diff_added_files", added_files)
        await self.render_tree_files("MODIFIED FILES", "cherry_files_diff_modified_files", modified_files)
        await self.render_tree_files("DELETED FILES", "cherry_files_diff_deleted_files", deleted_files)

    async def render_tree_files(self, label:str, label_class:str, files:list[str]) -> None:
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        await files_container.mount(Label(label, classes=label_class))
        if len(files) == 0:
            return
        await files_container.mount(Label("📂 root", classes="parent_directory"))
        tree = self.build_tree(files)
        await self.render_tree(tree)

    async def render_tree(self, tree, prefix=""):
        files_container = self.query_one("#files_scroll_container", VerticalScroll)
        entries = list(tree.items())
        for i, (name, subtree) in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = ""
            if is_last and not subtree:
                connector = "└── "
            elif subtree:
                connector = "├── 📂 "
            else:
                connector = "├── "
            #            connector = if is_last and not subtree elif subtree "-" else "├── "
            classes = "parent_directory" if subtree else ""
            await files_container.mount(Label(prefix + connector + name, classes=classes))
            self.log(prefix + connector + name)
            if subtree:
                 extension = "    " if is_last else "│   "
                 await self.render_tree(subtree, prefix + extension)

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

    def build_tree(self,files:list[str]):
        tree = {}
        for path in files:
            node = tree
            parts = path.split("/")
            for part in parts:
                if part not in node:
                    node[part] = {}
                node = node[part]
        return tree





