# LYRA AI Core

This layer hosts intelligence-centric modules that can be reused by the backend.

## Modules

- `memory/`: embeddings, vector stores, recall policies.
- `decision/`: intent routing, tool selection, confidence scoring.
- `orchestration/`: planner/executor/memory multi-agent protocols.

Keep this layer framework-agnostic so it can serve API, desktop, or edge runtimes.
