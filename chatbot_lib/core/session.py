"""Conversation memory.

A Session just holds the running list of {"role", "content"} turns
plus an optional system prompt. It doesn't know about any provider —
ChatBot is the only thing that reads from it and feeds it into a
provider call. Kept separate so it can be swapped, persisted, or
inspected on its own.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union


class Session:
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        max_history: Optional[int] = None,
    ):
        """
        Args:
            system_prompt: Instructions sent with every request.
            max_history: Max number of *turn pairs* (user+assistant) to
                keep. Older turns are dropped first. None = unlimited.
        """
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self) -> List[Dict[str, str]]:
        """Full message list, without the system prompt (ChatBot adds that)."""
        return list(self.messages)

    def clear(self) -> None:
        self.messages = []

    def _trim(self) -> None:
        if self.max_history is not None:
            keep = self.max_history * 2  # each turn = 1 user + 1 assistant
            if len(self.messages) > keep:
                self.messages = self.messages[-keep:]

    def save(self, path: Union[str, Path]) -> None:
        data = {"system_prompt": self.system_prompt, "messages": self.messages}
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Session":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        session = cls(system_prompt=data.get("system_prompt"))
        session.messages = data.get("messages", [])
        return session

    def __len__(self) -> int:
        return len(self.messages)
