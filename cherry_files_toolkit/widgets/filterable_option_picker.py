from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Input, OptionList


class FilterableOptionPicker(Vertical):
    DEFAULT_CSS = """
        FilterableOptionPicker {
            height: auto;
        }

        .filterable_option_picker_unit {
            height: auto;
        }

        /* The label sits as a title centred on the search input's border. */
        FilterableOptionPicker #search {
            border: round $primary;
            border-title-align: center;
            border-title-color: $primary;
            border-title-style: bold;
        }

        FilterableOptionPicker #search:focus {
            border: round $primary-lighten-2;
        }

        /* Bound the list so it scrolls internally instead of growing to
           fit every branch and inflating the row it lives in. */
        FilterableOptionPicker #options {
            height: auto;
            max-height: 8;
            border: round $primary;
            padding: 0;
        }

        FilterableOptionPicker #options:focus {
            border: round $primary-lighten-2;
        }
    """

    def __init__(self, label:str, items: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.items = items or []


    def compose(self) -> ComposeResult:
        with Vertical(classes="filterable_option_picker_unit"):
            search = Input(suggester=SuggestFromList(self.items, case_sensitive=False), id="search")
            search.border_title = self.label
            yield search
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
