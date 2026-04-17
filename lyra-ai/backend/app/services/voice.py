from __future__ import annotations

import asyncio


class VoiceEngine:
    """Placeholder voice synthesis layer for gTTS/ElevenLabs integration."""

    async def speak(self, text: str) -> str:
        await asyncio.sleep(0.05)
        return text
