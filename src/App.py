from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, RadioSet, RadioButton, Button, Static

from Utils import set_dotenv, get_dotenv

from Chat import Chat


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


class FitnessAgent(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "FitnessAgent.css"

    def on_mount(self) -> None:
        self.push_screen(Chat())

        # only shows the profile form if frequency or level is not set
        if not get_dotenv("frequency") or not get_dotenv("level"):
            self.push_screen(Profile())

    def action_toggle_dark(self) -> None:
        # An action to toggle dark mode
        self.dark = not self.dark


if __name__ == "__main__":
    app = FitnessAgent()
    app.run()
