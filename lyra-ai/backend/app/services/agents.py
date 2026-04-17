from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import quote_plus
from wikipedia import summary

from .music_library import music


@dataclass
class Plan:
    actions: List[str]
    final_prompt: str


class PlannerAgent:
    """Turns user text into a coarse plan with multiple actions."""

    def plan(self, text: str) -> Plan:
        pieces = [
            part.strip()
            for part in re.split(r"\s*(?:,| and then | then | and | & )\s*", text, flags=re.IGNORECASE)
            if part.strip()
        ]
        actions = pieces if pieces else [text]
        return Plan(actions=actions, final_prompt=text)


class ExecutorAgent:
    """Executes deterministic utility actions and returns a structured result."""

    def execute(self, action: str) -> Dict[str, str]:
        lowered = action.lower()
        normalized = " ".join(lowered.split())

        # Your original command intents (including Hindi trigger phrases).
        if "model" in normalized or "moodle" in normalized:
            return {"kind": "open_url", "payload": "https://cet.iitp.ac.in"}
        if "open instagram" in normalized or "instagram khol" in normalized:
            return {"kind": "open_url", "payload": "https://instagram.com"}
        if "open youtube" in normalized or "youtube khol" in normalized:
            return {"kind": "open_url", "payload": "https://youtube.com"}
        if "open github" in normalized or "coders ka adda" in normalized:
            return {"kind": "open_url", "payload": "https://github.com"}
        if "open linkedin" in normalized or "demotivate kar" in normalized:
            return {"kind": "open_url", "payload": "https://linkedin.com"}
        if "meri playlist chala" in normalized:
            return {
                "kind": "open_url",
                "payload": "https://youtu.be/AbkEmIgJMcU?si=V6ETJmVWDU2zOEtq",
            }

        # Search / Google flow.
        if normalized.startswith("search ") or normalized.startswith("google "):
            query = action.split(" ", 1)[1].strip() if " " in action else ""
            if query:
                return {
                    "kind": "open_url",
                    "payload": f"https://www.google.com/search?q={quote_plus(query)}",
                }
            return {"kind": "ask_search_topic", "payload": "Kya Search Karu?"}
        if "google" in normalized or "search" in normalized:
            return {"kind": "ask_search_topic", "payload": "Kya Search Karu?"}

        # Wikipedia/info flow.
        if (
            "information" in normalized
            or "tell me about" in normalized
            or normalized.startswith("who is ")
        ):
            query = (
                action.replace("tell me about", "")
                .replace("information", "")
                .replace("who is", "")
                .strip()
            )
            if query:
                try:
                    info = summary(query, sentences=2, auto_suggest=True)
                    return {"kind": "speak_text", "payload": info}
                except Exception:
                    return {"kind": "speak_text", "payload": "Sorry, I couldn't find anything on that."}
            return {"kind": "ask_info_topic", "payload": "Kya Jan na hai apko?"}

        # Lightweight "play <song>" support.
        if normalized.startswith("play "):
            song = normalized.replace("play", "", 1).strip()
            if song:
                if song in music:
                    return {"kind": "open_url", "payload": music[song]}
                close = difflib.get_close_matches(song, list(music.keys()), n=1, cutoff=0.75)
                if close:
                    return {"kind": "open_url", "payload": music[close[0]]}
                return {"kind": "speak_text", "payload": "Ye song play list mai nahi h"}
            return {"kind": "open_url", "payload": "https://music.youtube.com"}

        if "tum best ho" in normalized:
            return {"kind": "speak_text", "payload": "Thank you boss. Always at your service."}
        if "good bye" in normalized:
            return {"kind": "speak_text", "payload": "Good bye boss. LYRA signing off."}
        if "exit" in normalized or "quit" in normalized:
            return {"kind": "speak_text", "payload": "Good bye boss, LYRA going offline."}
        if "weather" in lowered:
            return {"kind": "realtime_hint", "payload": "Weather API hook available."}
        return {"kind": "none", "payload": ""}
