from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Dict, List

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class LyraBrain:
    """LLM adapter with a safe local fallback when no key is set."""

    def __init__(self) -> None:
        self._client = None
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        key = os.getenv("OPENAI_API_KEY")
        if key and OpenAI:
            self._client = OpenAI(api_key=key)

    async def respond(self, text: str, context: List[Dict[str, str]]) -> str:
        if not self._client:
            return self._local_assistant_reply(text)

        history = []
        for turn in context[-6:]:
            history.extend(
                [
                    {"role": "user", "content": turn["user"]},
                    {"role": "assistant", "content": turn["assistant"]},
                ]
            )

        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are LYRA. Speak like a premium voice assistant similar to Google Assistant: "
                        "clear, friendly, concise, action-first. Avoid debug-style wording."
                    ),
                },
                *history,
                {"role": "user", "content": text},
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content or "I am processing that now."

    def _local_assistant_reply(self, text: str) -> str:
        lowered = text.lower().strip()
        compact = re.sub(r"\s+", " ", lowered)
        tod = self._time_of_day_phrase()

        if "open youtube" in compact or "youtube khol" in compact:
            return f"{tod} Opening YouTube now."
        if "open instagram" in compact or "instagram khol" in compact:
            return f"{tod} Opening Instagram."
        if "open github" in compact or "coders ka adda" in compact:
            return f"{tod} Opening GitHub."
        if "open linkedin" in compact or "demotivate kar" in compact:
            return "Opening LinkedIn."
        if "moodle" in compact or "model" in compact:
            return "Opening Moodle portal."
        if compact.startswith("play "):
            song = compact.replace("play", "", 1).strip()
            return f"Playing {song} on YouTube." if song else "Playing your music."
        if "search" in compact or compact.startswith("google "):
            return "Got it. Searching Google."
        if "who is" in compact or "tell me about" in compact or "information" in compact:
            return "Sure. Fetching that information."
        if "weather" in compact:
            return "Checking the weather."
        if "good bye" in compact or "quit" in compact or "exit" in compact:
            return "Goodbye. I will be here when you need me."
        if "tum best ho" in compact:
            return "Thanks. Happy to help."
        return "Alright. Working on it."

    def _time_of_day_phrase(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning."
        if 12 <= hour < 17:
            return "Good afternoon."
        if 17 <= hour < 22:
            return "Good evening."
        return "Hello."
