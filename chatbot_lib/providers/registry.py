"""Maps a model name string to the provider class that handles it.

This is the piece that lets a user write:
    ChatBot(model="gpt-4o", api_key="...")
    ChatBot(model="claude-sonnet-4-6", api_key="...")
    ChatBot(model="llama3")   # no api_key needed, runs locally
and have the right adapter picked automatically.
"""

from typing import List, Tuple, Type

from ..exceptions import UnsupportedModelError
from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

# Order matters only in that the first matching prefix wins.
_PREFIX_MAP: List[Tuple[Tuple[str, ...], Type[BaseProvider]]] = [
    (("gpt-", "chatgpt", "o1", "o3", "o4"), OpenAIProvider),
    (("claude-",), AnthropicProvider),
    (("llama", "mistral", "gemma", "phi", "qwen", "deepseek"), OllamaProvider),
]


def get_provider_class(model: str) -> Type[BaseProvider]:
    model_lower = model.lower()
    for prefixes, provider_cls in _PREFIX_MAP:
        if any(model_lower.startswith(p) for p in prefixes):
            return provider_cls

    supported = ", ".join(p for group, _ in _PREFIX_MAP for p in group)
    raise UnsupportedModelError(
        f"No provider found for model '{model}'. "
        f"Recognized name prefixes: {supported}. "
        "For a local model not listed here, pass provider='ollama' explicitly."
    )


def register_provider(prefixes: Tuple[str, ...], provider_cls: Type[BaseProvider]) -> None:
    """Let advanced users plug in their own provider at runtime, e.g.:
    register_provider(("gemini-",), MyGeminiProvider)
    """
    _PREFIX_MAP.insert(0, (prefixes, provider_cls))
