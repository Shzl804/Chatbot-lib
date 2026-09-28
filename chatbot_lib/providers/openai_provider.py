"""OpenAI adapter (covers GPT-4, GPT-4o, GPT-3.5, o1, o3, etc.)."""

from typing import Dict, Generator, List, Optional

from ..exceptions import MissingDependencyError, ProviderError
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        try:
            import openai
        except ImportError as e:
            raise MissingDependencyError(
                "The 'openai' package is required for OpenAI models. "
                "Install it with: pip install chatbot-lib[openai]"
            ) from e
        self._client = openai.OpenAI(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model, messages=messages, **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise ProviderError(f"OpenAI request failed: {e}") from e

    def stream_chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Generator[str, None, None]:
        try:
            stream = self._client.chat.completions.create(
                model=self.model, messages=messages, stream=True, **kwargs
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            raise ProviderError(f"OpenAI streaming failed: {e}") from e
