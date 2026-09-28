"""Example: print the reply as it streams in, token by token."""

import os

from chatbot_lib import ChatBot

bot = ChatBot(model="claude-sonnet-4-6", api_key=os.environ.get("ANTHROPIC_API_KEY"))

for chunk in bot.stream("Write a 3-line poem about rivers."):
    print(chunk, end="", flush=True)
print()
