import openai
from typing import Dict, List
import pandas as pd

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Markdown, TabbedContent, RadioSet, RadioButton, Label

from Profile import Profile
from Chat import Chat


class FitnessAgent(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "FitnessAgent.css"
    data = pd.read_csv("template_prompts.csv")

    def compose(self) -> ComposeResult:
        # Create child widgets for the app
        yield Header(show_clock=True)

        # TODO : ajouter vérification
        yield Profile(id="profile")

        # TODO: ajouter changement de contexte
        yield Chat()

        # TODO: garder en bas
        yield Input(placeholder="Type your message here", id="user_input")
        yield Footer()

    def action_toggle_dark(self) -> None:
        # An action to toggle dark mode
        self.dark = not self.dark

    def generate_response(self, messages: List[Dict]) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response = completion.choices[0].message.content
        return response

    def add_chat_history(self, prompt, role="user"):
        self.chat_history.append({"role": role, "content": prompt})

    # key is the command selected by the user (e.g. "create_plan, add_workout, ...")
    def commands_prompt(self, key):
        df = self.data[self.data['template'] == key]

        system_content = df[df['role'] == 'system'].content.iloc[0]
        assistant_content = df[df['role'] == 'assistant'].content.iloc[0]
        user_content = df[df['role'] == 'user'].content.iloc[0]

        return self.generate_response(
            [{'role': 'system', 'content': system_content}, {'role': 'assistant', 'content': assistant_content},
             {'role': 'user', 'content': user_content}])

    def template_prompt(self, inputs: Dict[str, str], template: str) -> str:
        prompt = template.format(**inputs)
        return prompt

    # Fonction pour créer le plan d'entraînement original du user selon son niveau de fitness et sa fréquence
    # d'entraînement
    def user_plan(self, fitness_level, training_frequency):
        template = "Please create a workout plan. I am a {fitness_level}. I can train {training_frequency} times a week."
        {'fitness_level': fitness_level, 'training_frequency': training_frequency}
        return self.template_prompt({'fitness_level': fitness_level, 'training_frequency': training_frequency},
                                    template)


if __name__ == "__main__":
    app = FitnessAgent()
    app.run()
