from textual.app import App, ComposeResult
from textual.containers import Horizontal

# from modules.cherry_files_diff import CherryFilesDiff
from modules.cherry_files_picker import CherryFilesPicker

class MyApp(App):
    CSS_PATH = "my_app.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            # yield CherryFilesDiff()
            yield CherryFilesPicker()

if __name__ == "__main__":
    app = MyApp()
    app.run()
