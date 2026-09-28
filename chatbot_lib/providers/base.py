"""Provider interface.

Every LLM backend (OpenAI, Anthropic, local Ollama models, and any
future addition) implements this same interface. The ChatBot class
never needs to know which one it's talking to — that's the whole
point of the abstraction.
"""

from abc import ABC, abstractmethod
from typing import Dict, Generator, List, Optional


class BaseProvider(ABC):
    """Abstract adapter between ChatBot and a specific LLM API."""

    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.extra_config = kwargs

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send messages, return the full reply as a string (blocking)."""
        raise NotImplementedError

    @abstractmethod
    def stream_chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Generator[str, None, None]:
        """Send messages, yield the reply incrementally, chunk by chunk."""
        raise NotImplementedError
