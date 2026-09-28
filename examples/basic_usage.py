"""Minimal example: cloud model, one-off question + a short conversation."""

import os

from chatbot_lib import ChatBot

# Reads your key from an env var so you never hardcode it in source.
api_key = os.environ.get("OPENAI_API_KEY")

bot = ChatBot(
    model="gpt-4o-mini",
    api_key=api_key,
    system_prompt="You are a concise, friendly assistant.",
)

print(bot.chat("What is the capital of Pakistan?"))
print(bot.chat("What's its population, roughly?"))  # remembers previous turn

# Save the conversation to disk and reload it later.
bot.save_session("conversation.json")
