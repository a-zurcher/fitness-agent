# fitness-agent

Un agent IA pour le fitness, basé sur `ChatGPT`, construit avec [Textural](https://textual.textualize.io).

## Installation

1. Installer Python sur sa machine

2. Cloner ce dépôt git sur sa machine

   ```bash
   $ git clone https://github.com/a-zurcher/fitness-agent
   ```

3. Créer un environnement virtuel Python:

   ```bash
   $ python -m venv /path/to/fitness-agent
   ```

4. Activer environnement virtuel:

   - Mac OS / Linux

     ```bash
     $ cd /path/to/fitness-agent
     $ source venv/bin/activate
     ```

   - Windows (Powershell)

     ```powershell
     $ cd \path\to\fitness-agent
     $ venv\Scripts\activate
     ```

5. Installer les dépendances:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Faire une copie du fichier .env.example :

   ```
   $ cp .env.example .env
   ```

7. Ajouter [la clé](https://beta.openai.com/account/api-keys) OpenAI dans le nouveau fichier `.env`:

   ```bash
   OPENAI_API_KEY=YOUR_KEY_HERE
   ```

8. Pour lancer l'application :

   ```bash
   python app.py
   ```