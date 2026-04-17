from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .schemas import AnimationState, CommandEnvelope
from .services.agents import ExecutorAgent, PlannerAgent
from .services.llm import LyraBrain
from .services.memory import MemoryAgent
from .services.voice import VoiceEngine

app = FastAPI(title="LYRA Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

brain = LyraBrain()
memory = MemoryAgent()
planner = PlannerAgent()
executor = ExecutorAgent()
voice = VoiceEngine()


def _action_summary(action_results: list[dict[str, str]]) -> str:
    opened = [a["payload"] for a in action_results if a.get("kind") == "open_url" and a.get("payload")]
    spoken = [a["payload"] for a in action_results if a.get("kind") == "speak_text" and a.get("payload")]
    prompts = [a["payload"] for a in action_results if a.get("kind") in {"ask_search_topic", "ask_info_topic"}]
    if prompts:
        return prompts[0]
    if spoken:
        return spoken[0]
    if opened:
        if len(opened) == 1:
            return "Done."
        return f"Done. I handled {len(opened)} actions."
    return ""


def _event(state: AnimationState, text: str = "", event_type: str = "state") -> str:
    return json.dumps({"type": event_type, "state": state, "text": text})


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "online", "assistant": "LYRA"})


@app.get("/predictive-suggestion")
async def predictive_suggestion() -> JSONResponse:
    pref = memory.preference("music") or "lo-fi focus mix"
    suggestion = f"Want me to open YouTube and start your {pref}?"
    return JSONResponse({"suggestion": suggestion})


@app.websocket("/ws/assistant")
async def assistant_socket(ws: WebSocket) -> None:
    await ws.accept()
    pending_mode = ""
    try:
        await ws.send_text(_event("idle", "LYRA core online.", "boot"))
        while True:
            payload = await ws.receive_text()
            envelope = CommandEnvelope.model_validate_json(payload)
            text = envelope.text.strip()

            await ws.send_text(_event("listening", text))
            await ws.send_text(_event("thinking", "Analyzing multi-command intent."))

            if pending_mode == "search":
                plan = planner.plan(f"google {text}")
                pending_mode = ""
            elif pending_mode == "info":
                plan = planner.plan(f"tell me about {text}")
                pending_mode = ""
            else:
                plan = planner.plan(text)
            action_results = [executor.execute(a) for a in plan.actions]
            if any(r["kind"] == "open_url" for r in action_results):
                await ws.send_text(json.dumps({"type": "action", "state": "thinking", "actions": action_results}))
            if any(r["kind"] == "ask_search_topic" for r in action_results):
                pending_mode = "search"
            if any(r["kind"] == "ask_info_topic" for r in action_results):
                pending_mode = "info"

            response = await brain.respond(plan.final_prompt, memory.context())
            concise_action_reply = _action_summary(action_results)
            if concise_action_reply:
                response = concise_action_reply if response in {"Alright. Working on it.", "Done."} else response
            memory.remember_turn(text, response)

            spoken = await voice.speak(response)
            await ws.send_text(_event("speaking", spoken))
            await ws.send_text(_event("idle"))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await ws.send_text(_event("error", f"Runtime error: {exc}", "error"))
        except Exception:
            return


@app.get("/memory/export")
async def export_memory() -> JSONResponse:
    out = Path("memory_dump.json")
    out.write_text(json.dumps(memory.context(), indent=2), encoding="utf-8")
    return JSONResponse({"saved_to": str(out.resolve())})
