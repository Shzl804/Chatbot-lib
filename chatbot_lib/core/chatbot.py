"""The public-facing ChatBot class.

This is the one thing most users of the library will ever import:

    from chatbot_lib import ChatBot
    bot = ChatBot(model="gpt-4o", api_key="sk-...")
    print(bot.chat("Hello!"))

It ties together a provider (does the actual API call) and a Session
(remembers the conversation) behind one simple interface.
"""

from pathlib import Path
from typing import Generator, Optional, Type, Union

from ..providers import BaseProvider, get_provider_class    
from .session import Session


class ChatBot:
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_history: Optional[int] = None,
        provider: Optional[Type[BaseProvider]] = None,
        **provider_kwargs,
    ):
        """
        Args:
            model: Model name, e.g. "gpt-4o", "claude-sonnet-4-6", "llama3".
                The right provider is picked automatically from this name.
            api_key: API key for the chosen provider. Not needed for
                local models served through Ollama.
            system_prompt: Optional instructions sent with every message.
            max_history: Cap on remembered turn pairs (see Session).
            provider: Force a specific provider class instead of
                auto-detecting one from `model` (for custom/unlisted models).
            **provider_kwargs: Passed straight through to the provider's
                constructor (e.g. base_url= for a custom Ollama host).
        """
        self.model = model
        provider_cls = provider or get_provider_class(model)
        self.provider: BaseProvider = provider_cls(
            model=model, api_key=api_key, **provider_kwargs
        )
        self.session = Session(system_prompt=system_prompt, max_history=max_history)

    def chat(self, message: str, **kwargs) -> str:
        """Send a message, get the full reply back as a string."""
        self.session.add_user_message(message)
        reply = self.provider.chat(self._build_messages(), **kwargs)
        self.session.add_assistant_message(reply)
        return reply

    def stream(self, message: str, **kwargs) -> Generator[str, None, None]:
        """Send a message, yield the reply piece by piece as it arrives."""
        self.session.add_user_message(message)
        full_reply = []
        for chunk in self.provider.stream_chat(self._build_messages(), **kwargs):
            full_reply.append(chunk)
            yield chunk
        self.session.add_assistant_message("".join(full_reply))

    def reset(self) -> None:
        """Forget the conversation so far (system prompt is kept)."""
        self.session.clear()

    def save_session(self, path: Union[str, Path]) -> None:
        self.session.save(path)

    def load_session(self, path: Union[str, Path]) -> None:
        self.session = Session.load(path)

    def _build_messages(self):
        messages = []
        if self.session.system_prompt:
            messages.append({"role": "system", "content": self.session.system_prompt})
        messages.extend(self.session.get_messages())
        return messages

    def __repr__(self) -> str:
        return f"ChatBot(model={self.model!r}, turns={len(self.session)})"
 