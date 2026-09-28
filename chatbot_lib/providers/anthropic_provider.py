"""Anthropic adapter (covers Claude models).

Anthropic's API takes the system prompt as a separate top-level
argument rather than as a message in the list, so this adapter pulls
any {"role": "system", ...} message out before calling the SDK.
"""

from typing import Dict, Generator, List, Optional

from ..exceptions import MissingDependencyError, ProviderError
from .base import BaseProvider

DEFAULT_MAX_TOKENS = 1024


class AnthropicProvider(BaseProvider):
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        try:
            import anthropic
        except ImportError as e:
            raise MissingDependencyError(
                "The 'anthropic' package is required for Claude models. "
                "Install it with: pip install chatbot-lib[anthropic]"
            ) from e
        self._client = anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def _split_system(messages: List[Dict[str, str]]):
        system_prompt = None
        rest = []
        for m in messages:
            if m["role"] == "system" and system_prompt is None:
                system_prompt = m["content"]
            else:
                rest.append(m)
        return system_prompt, rest

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        system_prompt, rest = self._split_system(messages)
        max_tokens = kwargs.pop("max_tokens", DEFAULT_MAX_TOKENS)
        try:
            response = self._client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=rest,
                max_tokens=max_tokens,
                **kwargs,
            )
            return "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception as e:
            raise ProviderError(f"Anthropic request failed: {e}") from e

    def stream_chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Generator[str, None, None]:
        system_prompt, rest = self._split_system(messages)
        max_tokens = kwargs.pop("max_tokens", DEFAULT_MAX_TOKENS)
        try:
            with self._client.messages.stream(
                model=self.model,
                system=system_prompt,
                messages=rest,
                max_tokens=max_tokens,
                **kwargs,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise ProviderError(f"Anthropic streaming failed: {e}") from e
