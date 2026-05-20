import subprocess
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Label, Static

from widgets.filterable_option_picker import FilterableOptionPicker

class MyApp(App):
    CSS_PATH = "my_app.tcss"
    

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="section"):
                yield Static("Cherry Files Diff")
                with Horizontal():
                    yield FilterableOptionPicker(label="Divergent Branch", id="diff_divergent_branch")
                    yield FilterableOptionPicker(label="Base Branch", id="diff_base_branch")
                with Horizontal(classes="container"):
                    yield Static("Summary")
                with Horizontal(classes="container"):
                        yield Static("Diff Notes")
            with Vertical(classes="section"):
                yield Static("Cherry Files Picker")
                with Horizontal():
                    yield FilterableOptionPicker(label="Source Branch", id="picker_source_branch")
                    yield FilterableOptionPicker(label="Target Branch", id="picker_target_branch")

                with Horizontal(classes="container"):
                    with Vertical():
                        yield Static("Filters")
                        yield Label("Search:")
                        yield Input()

                with Horizontal():
                    with Vertical(classes="container"):
                        yield Static("Candidate Files")
                    with Vertical(classes="container"):
                        yield Static("Selected Files")
                with Horizontal(classes="container"):
                    yield Static("Preview highligted candidate file")
                with Horizontal(classes="container"):
                    yield Static("Commit")
                with Horizontal(classes="container"):
                    yield Static("Git Output")

    def on_mount(self) -> None:
        branches = self.get_branches()
        self.query_one("#diff_divergent_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#diff_base_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#picker_source_branch", FilterableOptionPicker).set_items(branches)
        self.query_one("#picker_target_branch", FilterableOptionPicker).set_items(branches)

    def get_branches(self):
        result = subprocess.run(["git", "branch", "-l"], capture_output = True, text=True)
        branches = [line.replace("*", "").strip() for line in result.stdout.splitlines()]
        return branches

if __name__ == "__main__":
    app = MyApp()
    app.run()
