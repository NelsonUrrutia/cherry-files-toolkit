from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, OptionList


class FilterableOptionPicker(Vertical):

    def __init__(self, label:str, items: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.items = items or []


    def compose(self) -> ComposeResult:
        with Vertical(classes="filterable_option_picker_unit"):
            yield Label(self.label)
            yield Input(suggester=SuggestFromList(self.items, case_sensitive=False), id="search")
            yield OptionList(id="options")

    def on_mount(self, ) -> None:
        self.sync_input_suggestions()
        self.sync_option_list()

    def set_items(self, items: list[str]) -> None:
        self.items = items
        self.sync_option_list()
        self.sync_input_suggestions()

    def sync_option_list(self) -> None:
        options = self.query_one("#options", OptionList)
        options.set_options(self.items)
        options.highlighted = 0 if self.items else None

    def sync_input_suggestions(self) -> None:
        search = self.query_one("#search", Input)
        search.suggester = SuggestFromList(self.items, case_sensitive=False)

    def get_search_value(self) -> str:
        return self.query_one("#search", Input).value

    @on(Input.Changed, "#search")
    def filter(self, event:Input.Changed) -> None:
        text = event.value.strip().lower()
        filtered = self.items if not text else [x for x in self.items if text in x.lower()]
        options = self.query_one("#options", OptionList)
        options.set_options(filtered)
        options.highlighted = 0 if filtered else None


    @on(OptionList.OptionSelected, "#options")
    def select(self, event: OptionList.OptionSelected) -> None:
        chosen = str(event.option.prompt)
        search = self.query_one("#search", Input)        
        search.value = chosen
        search.focus()
        search.action_end()
