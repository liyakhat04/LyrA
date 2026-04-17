from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List


class MemoryAgent:
    """Keeps lightweight conversation and preference memory in process."""

    def __init__(self, limit: int = 20) -> None:
        self._history: Deque[Dict[str, str]] = deque(maxlen=limit)
        self._preferences: Dict[str, str] = {}

    def remember_turn(self, user_text: str, assistant_text: str) -> None:
        self._history.append({"user": user_text, "assistant": assistant_text})

    def set_preference(self, key: str, value: str) -> None:
        self._preferences[key] = value

    def preference(self, key: str) -> str | None:
        return self._preferences.get(key)

    def context(self) -> List[Dict[str, str]]:
        return list(self._history)
