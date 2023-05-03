from textual.app import App

from Utils import get_dotenv

from Chat import Chat
from Profile import Profile


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
