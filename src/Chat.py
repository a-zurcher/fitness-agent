import dotenv
import openai
import pandas as pd
from textual import log, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import TextLog, Button, Input, Tabs, Header, Tab


class Chat(Screen):
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
        yield Header(show_clock=True)

        yield Tabs(
            Tab("Create plan", id="create_plan"),
            Tab("Add workout", id="add_workout"),
            Tab("Remove workout", id="remove_workout"),
            Tab("View plan", id="view_plan"),
            Tab("Edit workout", id="edit_workout"),
            active="create_plan"
        )

        yield TextLog(highlight=True, markup=True, wrap=True)

        yield Container(
            Input(placeholder="Type your message here", id="user_input"),
            Button("Submit", variant="primary", id="user_submit"),
            id="chat_input"
        )

    def _on_screen_resume(self) -> None:
        self.context = self.query_one(Tabs).active

        # focuses input
        user_input = self.query_one("#user_input")
        user_input.focus()

        plan = dotenv.get_key(key_to_get="plan", dotenv_path=".env")
        frequency = dotenv.get_key(key_to_get="frequency", dotenv_path=".env")
        level = dotenv.get_key(key_to_get="level", dotenv_path=".env")

        if not plan and frequency and level:
            # generates a new plan if frequency and level is set
            self.send_message("Create a new workout plan without additional comments. " + self.user_profile())
        elif plan and frequency and level:
            # if a plan is already present, shows it
            self.print_message("agent", dotenv.get_key(key_to_get="plan", dotenv_path=".env"))

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """On tab selection, sets global context to tab value"""
        self.context = event.tab.id

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

        # saves to chat history, with profile added
        self.add_to_chat_history(role, message)

    def chat_completion(self, key: str, save_plan: bool = True) -> None:
        """Sends a message to the API and receive a response"""
        openai.api_key = dotenv.dotenv_values(".env")['OPENAI_API_KEY']
        user_input = self.query_one("#user_input")
        user_submit = self.query_one("#user_submit")

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

        log("messages : ")
        log(messages)
        log("chat_history : ")
        log(self.chat_history)

        user_input.disabled = True
        user_input.value = ""
        user_submit.disabled = True

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=messages
        )
        response = completion.choices[0].message['content']

        user_input.disabled = False
        user_submit.disabled = False

        # saves the plan (if function set)
        if save_plan:
            dotenv.set_key(key_to_set="plan", value_to_set=str(response), dotenv_path=".env")

        # print the message
        self.print_message("agent", response)

    def user_profile(self) -> str:
        """creates new workout using fitness level and frequency preference"""
        level = dotenv.get_key(key_to_get="level", dotenv_path=".env")
        frequency = dotenv.get_key(key_to_get="frequency", dotenv_path=".env")

        return f"My level is {level}. " \
               f"I can train {frequency} times a week."
