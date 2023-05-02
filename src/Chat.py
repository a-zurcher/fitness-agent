import dotenv
import openai
import pandas as pd
from textual import log, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static, TextLog, Button, Input, Tabs, LoadingIndicator

class Chat(Static):
    data = pd.read_csv("template_prompts.csv")
    context = 0
    contexts = [
        "create_plan",
        "add_workout",
        "remove_workout",
        "view_plan",
        "edit_workout",
    ]

    chat_history = []

    def compose(self) -> ComposeResult:
        yield Tabs(
            # disabled=True
        )

        yield TextLog(highlight=True, markup=True, wrap=True)

        yield Container(
            Input(placeholder="Type your message here", id="user_input"),
            Button("Submit", variant="primary", id="user_submit"),
            id="chat_input"
        )

    def on_mount(self) -> None:
        self.context = "create_plan"

        # focuses input
        user_input = self.query_one("#user_input")
        user_input.focus()

        # Adds the tabs on mount
        tabs = self.query_one(Tabs)
        for c in self.contexts:
            tabs.add_tab(c)

        if not dotenv.get_key(key_to_get="plan", dotenv_path=".env"):
            # creates new workout
            level = dotenv.get_key(key_to_get="level", dotenv_path=".env")
            frequency = dotenv.get_key(key_to_get="frequency", dotenv_path=".env")
            self.send_message(self.user_plan(frequency, level))
        else:
            self.print_message("agent", dotenv.get_key(key_to_get="plan", dotenv_path=".env"))

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """On tab selection, sets global context to tab value"""
        self.context = event.tab.label.__str__()

    def on_input_submitted(self) -> None: self.send_message(self.query_one("#user_input").value)
    def on_button_pressed(self) -> None: self.send_message(self.query_one("#user_input").value)

    @work(exclusive=False)
    def send_message(self, message: str) -> None:
        # draws the message on the screen
        self.print_message("user", message)

        # sends the message to the API for completion
        self.chat_completion(self.context)

    def add_to_chat_history(self, role: str, message: str) -> None:
        self.chat_history.append({"role": role, "content": message})

    def print_message(self, role: str, message: str) -> None:
        """Used to print a message on the interface"""
        formatted_msg = ""

        match role:
            case "user":
                formatted_msg = "[bold white on blue]You[/bold white on blue][blue] " + message + "\n"
            case "agent":
                formatted_msg = "[bold white on magenta]Agent[/bold white on magenta][magenta] " + message + "\n"

        self.query_one(TextLog).write(formatted_msg)

        # saves to chat history
        self.add_to_chat_history(role, message)

    def chat_completion(self, key: str, save_plan: bool = True) -> None:
        """Sends a message to the API and receive a response"""
        openai.api_key = dotenv.dotenv_values(".env")['OPENAI_API_KEY']

        # key is the command selected by the user (e.g. "create_plan, add_workout, ...")
        df = self.data[self.data['template'] == key]

        system_content = df[df['role'] == 'system'].content.iloc[0]
        assistant_content = df[df['role'] == 'assistant'].content.iloc[0]
        user_content = df[df['role'] == 'user'].content.iloc[0]

        messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'assistant', 'content': assistant_content},
            {'role': 'user', 'content': user_content},
            self.chat_history[-1]
        ]

        log(messages)
        log(self.chat_history)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=messages
        )
        response = completion.choices[0].message['content']

        # saves the plan (if function set)
        if save_plan:
            dotenv.set_key(key_to_set="plan", value_to_set=str(response), dotenv_path=".env")

        # print the message
        self.print_message("agent", response)

    def user_plan(self, frequency, fitness_level) -> str:
        """creates new workout using fitness level and frequency preference"""
        return f"New workout plan. My level is {fitness_level}. " \
               f"I can train {frequency} times a week."


class Loading(Screen):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()