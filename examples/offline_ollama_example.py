"""Example: run fully offline with a local model, no API key, no internet.

Prerequisite:
    1. Install Ollama: https://ollama.com
    2. Pull a model:   ollama pull llama3
    3. Ollama runs a local server automatically on localhost:11434
"""

from chatbot_lib import ChatBot

bot = ChatBot(model="llama3")  # no api_key needed for local models

print(bot.chat("Give me one fun fact about dairy farming."))
