from textual.app import ComposeResult
from textual.widgets import Static, TextLog

class Chat(Static):
    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_ready(self) -> None:
        text_log = self.query_one(TextLog)
        text_log.write("bru")
