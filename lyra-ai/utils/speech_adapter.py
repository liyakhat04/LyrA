from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SpeechSettings:
    wake_word: str = "lyra"
    language: str = "en-IN"
    continuous: bool = True


def normalize_transcript(raw: str) -> str:
    """Normalize transcript for downstream command parsing."""
    return " ".join(raw.strip().lower().split())
