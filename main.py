from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import  Input, Label, Static

from modules.cherry_files_diff import CherryFilesDiff
from widgets.filterable_option_picker import FilterableOptionPicker

class MyApp(App):
    CSS_PATH = "my_app.tcss"
    

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield CherryFilesDiff()
            #with Vertical(classes="section"):
                #yield Static("Cherry Files Picker")
                #with Horizontal():
                    #yield FilterableOptionPicker(label="Source Branch", id="picker_source_branch")
                    #yield FilterableOptionPicker(label="Target Branch", id="picker_target_branch")
#
                #with Horizontal(classes="container"):
                    #with Vertical():
                        #yield Static("Filters")
                        #yield Label("Search:")
                        #yield Input()
#
                #with Horizontal():
                    #with Vertical(classes="container"):
                        #yield Static("Candidate Files")
                    #with Vertical(classes="container"):
                        #yield Static("Selected Files")
                #with Horizontal(classes="container"):
                    #yield Static("Preview highligted candidate file")
                #with Horizontal(classes="container"):
                    #yield Static("Commit")
                #with Horizontal(classes="container"):
                #    yield Static("Git Output")
   
if __name__ == "__main__":
    app = MyApp()
    app.run()
