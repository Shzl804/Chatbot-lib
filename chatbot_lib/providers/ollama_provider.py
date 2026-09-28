"""Ollama adapter — talks to a locally running Ollama server.

This is what makes the library usable fully offline: no API key,
no internet connection, no cost per token. It just needs Ollama
(https://ollama.com) running on the machine with the requested
model already pulled (e.g. `ollama pull llama3`).
"""

import json
from typing import Dict, Generator, List, Optional

import requests

from ..exceptions import ProviderError
from .base import BaseProvider

DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaProvider(BaseProvider):
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,  # unused, kept for a uniform constructor
        base_url: str = DEFAULT_BASE_URL,
        **kwargs,
    ):
        super().__init__(model, api_key, **kwargs)
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False, **kwargs},
                timeout=kwargs.pop("timeout", 120),
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except requests.exceptions.ConnectionError as e:
            raise ProviderError(
                "Couldn't reach Ollama. Is it running? Start it with `ollama serve` "
                f"(expected at {self.base_url})."
            ) from e
        except Exception as e:
            raise ProviderError(f"Ollama request failed: {e}") from e

    def stream_chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Generator[str, None, None]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True, **kwargs},
                stream=True,
                timeout=kwargs.pop("timeout", 120),
            )
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except requests.exceptions.ConnectionError as e:
            raise ProviderError(
                "Couldn't reach Ollama. Is it running? Start it with `ollama serve` "
                f"(expected at {self.base_url})."
            ) from e
        except Exception as e:
            raise ProviderError(f"Ollama streaming failed: {e}") from e
