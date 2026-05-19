import subprocess
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, Static, OptionList


class MyApp(App):
    CSS_PATH = "my_app.tcss"
    

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="section"):
                yield Static("Cherry Files Diff")
                with Horizontal():
                    with Vertical(classes="container"):
                        yield Label("Divergent branch")
                        yield Input(suggester=SuggestFromList(self.get_branches(), case_sensitive=False), id="divergent-branch-search")
                        yield OptionList(id="divergent-branch-options")
                    with Vertical(classes="container"):
                        yield Label("Base branch")
                        yield Input(suggester=SuggestFromList(self.get_branches(), case_sensitive=False), id="base-branch-search")
                        yield OptionList(id="base-branch-options")
                with Horizontal(classes="container"):
                    yield Static("Summary")
                with Horizontal(classes="container"):
                        yield Static("Diff Notes")
            with Vertical(classes="section"):
                yield Static("Cherry Files Picker")
                with Horizontal():
                    with Vertical(classes="container"):
                        yield Label("Source branch")
                        # yield Input(suggester=SuggestFromList(get_branches(), case_sensitive=False))
                    with Vertical(classes="container"):
                        yield Label("Target branch")
                        # yield Input(suggester=SuggestFromList(get_branches(), case_sensitive=False))
                with Horizontal(classes="container"):
                    with Vertical():
                        yield Static("Filters")
                        yield Label("Search:")
                        # yield Input(suggester=SuggestFromList(get_branches(), case_sensitive=False))

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
        self.branches = self.get_branches()
        self.query_one("#divergent-branch-options", OptionList).set_options(self.branches)
        self.query_one("#base-branch-options", OptionList).set_options(self.branches)
    
    @on(Input.Changed, "#base-branch-search")
    def filter_base_branch_search(self, event: Input.Changed) -> None:
        search_text = event.value.strip().lower()
        filtered = (
            self.branches
            if not search_text
            else [item for item in self.branches if search_text in item.lower()]
        )
        option_list = self.query_one("#base-branch-options", OptionList)
        option_list.set_options(filtered)
        option_list.highlighted = 0 if filtered else None

    @on(OptionList.OptionSelected, "#base-branch-options")
    def on_base_branch_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        chosen_text = str(event.option.prompt)
        inp = self.query_one(Input)
        inp.value = chosen_text

        inp.focus()
        inp.action_end()

    @on(Input.Changed, "#divergent-branch-search")
    def filter_divergent_branch_search(self, event: Input.Changed) -> None:
        search_text = event.value.strip().lower()
        filtered = (
            self.branches
            if not search_text
            else [item for item in self.branches if search_text in item.lower()]
        )
        option_list = self.query_one("#divergent-branch-options", OptionList)
        option_list.set_options(filtered)
        option_list.highlighted = 0 if filtered else None

    @on(OptionList.OptionSelected, "#divergent-branch-options")
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        chosen_text = str(event.option.prompt)
        inp = self.query_one(Input)
        inp.value = chosen_text

        inp.focus()
        inp.action_end()

    def get_branches(self):
        result = subprocess.run(["git", "branch", "-l"], capture_output = True, text=True)
        branches = [line.replace("*", "").strip() for line in result.stdout.splitlines()]
        return branches
    
if __name__ == "__main__":
    app = MyApp()
    app.run()
