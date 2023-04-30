from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, Label, RadioSet, RadioButton


class Profile(Static):
    def compose(self) -> ComposeResult:
        yield Container(FitnessLevel(), TrainingDays())


class FitnessLevel(Static):
    def compose(self) -> ComposeResult:
        yield Label("Please select your fitness level")
        with RadioSet(id="fitness_level"):
            yield RadioButton("Beginner")
            yield RadioButton("Medium")
            yield RadioButton("Advanced")


class TrainingDays(Static):
    def compose(self) -> ComposeResult:
        yield Label("Training: how many times can you train per week")
        with RadioSet(id="training_days"):
            for i in range(7):
                yield RadioButton(str(i + 1))
