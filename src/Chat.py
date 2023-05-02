import time

import openai
import pandas as pd
from textual import log, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import TextLog, Button, Input, Tabs, Header, Tab
from Utils import set_dotenv, get_dotenv


class Chat(Screen):
    data = pd.read_csv("template_prompts.csv")

    chat_history = []
    text_log_history = ""

    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("Create plan", id="create_plan"),
            Tab("Add workout", id="add_workout"),
            Tab("Remove workout", id="remove_workout"),
            Tab("View plan", id="view_plan"),
            active="create_plan"
        )

        yield TextLog(highlight=True, markup=True, wrap=True)

        yield Container(
            Input(placeholder="Type your message here", id="user_input"),
            Button("Submit", variant="primary", id="user_submit"),
            id="chat_input"
        )

    def _on_screen_resume(self) -> None:
        """Activates when Chat is on screen"""
        tabs = self.query_one(Tabs)
        self.context = tabs.active

        # focuses input
        user_input = self.query_one("#user_input")
        user_input.focus()

        plan = get_dotenv("plan")
        frequency = get_dotenv("frequency")
        level = get_dotenv("level")

        if not plan and frequency and level:
            # generates a new plan if frequency and level is set
            self.send_message("Create a new workout plan without additional comments. " + self.user_profile())
        elif plan and frequency and level:
            # if a plan is already present, shows it
            self.print_message("agent", get_dotenv("plan"))
            tabs.active = "view_plan"

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """On tab selection, sets global context to tab value"""
        self.context = event.tab.id
        if self.context == "view_plan":
            self.query_one("#user_input").disabled = True
            self.query_one("#user_submit").disabled = True
        else:
            self.query_one("#user_input").disabled = False
            self.query_one("#user_submit").disabled = False
            self.query_one("#user_input").focus()

    def on_input_submitted(self) -> None:
        self.send_message(self.query_one("#user_input").value)

    def on_button_pressed(self) -> None:
        self.send_message(self.query_one("#user_input").value)

    @work(exclusive=False)
    def send_message(self, message: str) -> None:
        """Prints messages, and sends query to API"""
        self.print_message("user", message)
        self.chat_completion(self.context)

    def add_to_chat_history(self, role: str, message: str) -> None:
        if role == "user" and get_dotenv("plan"):
            self.chat_history.append({"role": role, "content": self.user_profile() + "This is your last message : " + get_dotenv("plan") + ".\n" + message})
        else:
            self.chat_history.append({"role": role, "content": message})

    def print_message(self, role: str, message: str) -> None:
        """Used to print a message on the interface"""
        formatted_msg = ""

        match role:
            case "user":
                formatted_msg = "[bold black on white]You[/bold black on white][white] " + message + "\n"
            case "agent":
                formatted_msg = "[bold white on blue]Agent[/bold white on blue][blue] " + message + "\n"

        self.query_one(TextLog).write(formatted_msg)

        # saves to chat history, with profile added
        self.add_to_chat_history(role, message)

        # resets, then append to text_log_history variable
        self.text_log_history = ""
        self.text_log_history = self.text_log_history + formatted_msg + "\n"

    def chat_completion(self, key: str, save_plan: bool = True) -> None:
        """Sends a message to the API and receive a response"""
        openai.api_key = get_dotenv("OPENAI_API_KEY")
        user_input = self.query_one("#user_input")
        formatted_user_input = f"[bold black on white]You[/bold black on white][white] {user_input.value}\n\n"

        user_submit = self.query_one("#user_submit")
        text_log = self.query_one(TextLog)

        # key is the command selected by the user (e.g. "create_plan, add_workout, ...")
        df = self.data[self.data['template'] == key]

        system_content      = df[df['role'] == 'system'].content.iloc[0]
        assistant_content   = df[df['role'] == 'assistant'].content.iloc[0]
        user_content        = df[df['role'] == 'user'].content.iloc[0]

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
        user_submit.label = "Loading..."

        delay_time = 0.01

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=messages,
            stream=True
        )

        text = ""
        print_message = PrintMessage(role="agent", history=self.text_log_history, text_log=text_log)

        for event in completion:
            event_text = event['choices'][0]['delta']  # EVENT DELTA RESPONSE
            answer = event_text.get('content', '')  # RETRIEVE CONTENT

            text = text + answer
            # STREAM THE ANSWER
            print_message.stream(msg=answer)

            time.sleep(delay_time)

        user_input.disabled = False
        user_submit.disabled = False
        user_submit.label = "Submit"

        # response = completion.choices[0].message['content']

        if save_plan:
            set_dotenv("plan", text)

        self.text_log_history = self.text_log_history + f"[bold white on blue]Agent[/bold white on blue][blue]{text}\n"

        

    def user_profile(self) -> str:
        """keeps the fitness level and frequency preference"""
        level = get_dotenv("level")
        frequency = get_dotenv("frequency")

        return f"My fitness level is {level}. " \
               f"I can train {frequency} times a week."


class PrintMessage:
    """Utility class to print text in stream"""
    history = ""
    text_log = None

    def __init__(self, role: str, history: str, text_log: TextLog):
        self.history = history
        self.text_log = text_log

        match role:
            case "user":
                self.history = self.history + "[bold black on white]You[/bold black on white][white] "
            case "agent":
                self.history = self.history + "[bold white on blue]Agent[/bold white on blue][blue] "

    def stream(self, msg: str):
        """Used to print a message on the interface"""
        self.history = self.history + msg

        self.text_log.clear()
        self.text_log.write(self.history + "\n")

    def static(self, msg: str):
        """Used to print a message on the interface"""
        self.text_log.write(self.history + msg + "\n")
