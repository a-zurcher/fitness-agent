import dotenv
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, RadioSet, RadioButton, Button, Static

from Chat import Chat


class Profile(Screen):
    def compose(self):
        yield self.ProfileLevel()
        yield self.ProfileFrequency()

        yield Button("Submit", variant="primary", id="profile_submit")

    def on_button_pressed(self) -> None:
        if dotenv.get_key(key_to_get="level", dotenv_path=".env") and \
                dotenv.get_key(key_to_get="frequency", dotenv_path=".env"):
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
            level = event.pressed.label.__str__()
            dotenv.set_key(key_to_set="level", value_to_set=level, dotenv_path=".env")

    # Manages how many training days question
    class ProfileFrequency(Static):
        max_frequency = 7

        def compose(self) -> ComposeResult:
            yield Label("[bold]Frequency: how many times can you train per week :")
            with RadioSet(id="frequency"):
                for i in range(self.max_frequency):
                    yield RadioButton(str(i + 1))

        def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
            frequency = event.pressed.label.__str__()
            dotenv.set_key(key_to_set="frequency", value_to_set=frequency, dotenv_path=".env")


class FitnessAgent(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "FitnessAgent.css"

    def compose(self) -> ComposeResult:
        # Create child widgets for the app
        yield Header(show_clock=True)

        yield Chat()

    def on_mount(self) -> None:
        level = dotenv.get_key(dotenv_path=".env", key_to_get="level")
        frequency = dotenv.get_key(dotenv_path=".env", key_to_get="frequency")

        if not level or not frequency:
            self.push_screen(Profile())

    def action_toggle_dark(self) -> None:
        # An action to toggle dark mode
        self.dark = not self.dark


if __name__ == "__main__":
    app = FitnessAgent()
    app.run()
