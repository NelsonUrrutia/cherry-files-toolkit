from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, Static


branch_examples = [
    "main",
    "dev",
    "feature/search-catalog",
    "fix/css-improvements",
    "feature/ai-integration"
]

class MyApp(App):
    CSS_PATH = "my_app.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="section"):
                yield Static("Cherry Files Diff")
                with Horizontal():
                    with Vertical(classes="container"):
                        yield Label("Divergent branch")
                        yield Input(suggester=SuggestFromList(branch_examples, case_sensitive=False))
                    with Vertical(classes="container"):
                        yield Label("Base branch")
                        yield Input(suggester=SuggestFromList(branch_examples, case_sensitive=False))
                with Horizontal(classes="container"):
                    yield Static("Summary")
                with Horizontal(classes="container"):
                        yield Static("Diff Notes")
            with Vertical(classes="section"):
                yield Static("Cherry Files Picker")
                with Horizontal():
                    with Vertical(classes="container"):
                        yield Label("Source branch")
                        yield Input(suggester=SuggestFromList(branch_examples, case_sensitive=False))
                    with Vertical(classes="container"):
                        yield Label("Target branch")
                        yield Input(suggester=SuggestFromList(branch_examples, case_sensitive=False))
                with Horizontal(classes="container"):
                    with Vertical():
                        yield Static("Filters")
                        yield Label("Search:")
                        yield Input(suggester=SuggestFromList(branch_examples, case_sensitive=False))

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

if __name__ == "__main__":
    app = MyApp()
    app.run()
