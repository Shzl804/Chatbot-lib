"""chatbot_lib — a beginner-friendly, provider-agnostic chatbot library.

    from chatbot_lib import ChatBot

    bot = ChatBot(model="gpt-4o", api_key="sk-...")
    print(bot.chat("Hello!"))

    # Or run fully offline with a local model via Ollama, no key needed:
    bot = ChatBot(model="llama3")
    print(bot.chat("Hello!"))
"""

from .core.chatbot import ChatBot
from .core.session import Session
from .exceptions import (
    ChatbotLibError,
    MissingDependencyError,
    ProviderError,
    UnsupportedModelError,
)
from .providers.registry import register_provider

__version__ = "0.1.0"

__all__ = [
    "ChatBot",
    "Session",
    "ChatbotLibError",
    "UnsupportedModelError",
    "ProviderError",
    "MissingDependencyError",
    "register_provider",
]
