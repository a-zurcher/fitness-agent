from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, RadioSet, Label, RadioButton

from Utils import get_dotenv, set_dotenv


class Profile(Screen):
    def compose(self):
        yield self.ProfileLevel()
        yield self.ProfileFrequency()

        yield Button("Submit", variant="primary", id="profile_submit")

    def on_button_pressed(self) -> None:
        if get_dotenv("level") and get_dotenv("frequency"):
            self.app.pop_screen()

    # Manages fitness level question
    class ProfileLevel(Static):
        levels = ["Beginner", "Intermediate", "Advanced"]

        def compose(self) -> ComposeResult:
            yield Label("[bold]Please select your fitness level :")
            with RadioSet(id="fitness_level"):
                for l in self.levels:
                    yield RadioButton(l)

        def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
            set_dotenv("level", event.pressed.label.__str__())

    # Manages how many training days question
    class ProfileFrequency(Static):
        max_frequency = 7

        def compose(self) -> ComposeResult:
            yield Label("[bold]Frequency: how many times can you train per week :")
            with RadioSet(id="frequency"):
                for i in range(self.max_frequency):
                    yield RadioButton(str(i + 1))

        def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
            set_dotenv("frequency", event.pressed.label.__str__())