from typing import Literal

from pydantic import BaseModel


AnimationState = Literal["idle", "listening", "thinking", "speaking", "error"]


class CommandEnvelope(BaseModel):
    text: str
    source: str = "voice"


class EventEnvelope(BaseModel):
    type: str
    state: AnimationState
    text: str = ""
