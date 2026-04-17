# LYRA AI - Cinematic Voice Assistant

LYRA is a futuristic, JARVIS-inspired full-stack assistant with real-time animation state sync, voice command flow, and multi-agent backend orchestration.

## Project Structure

```text
lyra-ai/
  frontend/   # React + Three.js + Framer Motion + Tailwind HUD UI
  backend/    # FastAPI + WebSocket runtime + multi-agent orchestration
  ai-core/    # intelligence architecture modules
  utils/      # reusable integrations and system helpers
```

## Features Included

- Real-time WebSocket bridge (`frontend <-> backend`)
- Animation states: `idle`, `listening`, `thinking`, `speaking`, `error`
- Neon glassmorphism 3D orb with ambient particle field
- Voice wake-style command capture in browser (`Lyra ...`)
- Multi-command planning and execution pipeline
- Memory agent (conversation + preference hooks)
- LLM adapter with local fallback mode when API key is missing
- Predictive suggestion endpoint

## Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Available endpoints:

- `GET /health`
- `GET /predictive-suggestion`
- `GET /memory/export`
- `WS /ws/assistant`

## Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Voice Flow

1. Browser continuously listens (Web Speech API fallback).
2. Speak command prefixed with wake phrase, e.g. `Lyra open YouTube and play lofi`.
3. Frontend streams text command to backend WebSocket.
4. Backend emits state events and response text.
5. Frontend updates orb behavior and waveform in real time.

## Where To Extend Next

- Plug in Whisper streaming for robust voice input.
- Plug in ElevenLabs in `backend/app/services/voice.py`.
- Add FAISS or Pinecone in `ai-core/memory`.
- Add OS control adapters inside `utils/`.
- Add screen awareness module (OCR/capture pipeline).
- Add planner confidence and tool-router scoring.

## Notes

- Current system control actions are scaffolded and intentionally safe.
- LLM works in fallback mode unless `OPENAI_API_KEY` is set.
