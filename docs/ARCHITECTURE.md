# Architecture

## Open-source leverage

Do not reinvent commodity engines. See [OSS.md](OSS.md) for locked defaults (Whisper, Piper, Home Assistant, sqlite-vec, Flet, etc.).

## Components

### Central brain

- FastAPI (planned) service hosting API, WebSocket, agent runtime
- Holds LLM provider keys
- Source of truth for memories, sessions, tool connections, action log

### Soul

- Profile + memory store
- Retrieval into system prompt each turn
- Persona config

### Mind

- Planner / tool-calling loop
- Confirmation gate
- Streaming responses to clients

### Hands

- Tool protocol (name, schema, risk level, executor)
- Device bridges (run on clients, orchestrated by brain)
- Cloud/API tools (run on brain)
- Home tools (via house hub / Home Assistant bridge)

### Presence clients

- Thin UI + sensors + local permissions
- Forward utterances/events to brain
- Execute device-local tool calls when asked
- Cache for offline / latency
- Windows presence uses a **Python/Flet desktop UI** with tray support (not a Textual TUI; see ADR-0021, ADR-0008 superseded)
- Android presence stays native-first; keep UI slices small enough for mini workers

### House body

- Always-on node (often same machine as brain)
- Room audio endpoints
- IoT bridge

### Sync

- REST + WebSocket
- Entities: `updated_at`, `device_id`
- v1 conflict: last-write-wins

## Data (conceptual)

- users / devices
- messages / sessions
- memories
- action_log
- tool_connections
- home_devices
- synced domain entities (as plugins need them)

## Security boundaries

See [SECURITY.md](SECURITY.md). Clients never embed provider API keys.

## Build-time architecture

The **docs + board + `devloop`** are the meta-control plane for implementing this system with AI agents. They are not runtime product components.
