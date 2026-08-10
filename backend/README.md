# Backend — Jarvis Brain

Central brain service. FastAPI + SQLite + Gemini. Runs on your always-on host (PC, home hub, Raspberry Pi).

## Run

```bash
# 1. Copy and fill .env
cp .env.example .env
# Add your GEMINI_API_KEY (free at https://aistudio.google.com/app/apikey)

# 2. Install deps
pip install -r backend/requirements.txt

# 3. Start
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787 --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Brain info |
| GET | `/health` | Status + LLM readiness |
| POST | `/chat` | SSE streaming chat |
| WS | `/ws` | WebSocket chat |
| GET | `/soul/memories` | List all memories |
| PUT | `/soul/memories/{key}` | Upsert a memory |
| DELETE | `/soul/memories/{key}` | Delete a memory |
| GET | `/soul/habits` | List learned habits |
| DELETE | `/soul/habits/{id}` | Archive a habit |
| GET | `/soul/persona` | Current persona + system prompt preview |
| PATCH | `/soul/persona` | Rename the assistant |
| GET | `/tools` | List registered tools |
| GET | `/hands/actions` | Tool execution audit log (redacted params) |
| GET | `/sync/status` | Connected WS client count |
| POST | `/pair` | Device pairing stub → token |
| GET | `/pair/me` | Validate current token |
| GET | `/docs` | Interactive API docs (Swagger) |

## Home Assistant bridge (Phase 5)

The brain can control Home Assistant devices (e.g. lights) through a plugin. Requires a running Home Assistant instance and a long-lived access token.

```bash
# Add to your .env (see backend/app/config.py)
JARVIS_HA_URL=http://192.168.1.10:8123
JARVIS_HA_TOKEN=<long-lived-token-from-HA-profile>
JARVIS_HA_ENTITY=light.living_room   # optional default entity
```

Tools (registered on startup via `discover_plugins`):

| Tool | Risk | What it does |
|------|------|--------------|
| `home_entity_list` | auto | List HA entities + states (read-only) |
| `home_entity_set` | confirm_once | Turn an entity on/off, optional brightness 0-255 |

If HA is unconfigured, these tools fail visibly with a clear error. See `backend/plugins/homeassistant/__init__.py` and ADR-0019.

## Rename the AI

```bash
# Via .env (restart needed)
ASSISTANT_NAME=Friday

# Via API (live, no restart)
curl -X PATCH http://localhost:8787/soul/persona \
  -H "Content-Type: application/json" \
  -d '{"name": "Friday"}'
```

## Quick test

```bash
# Health
curl http://localhost:8787/health

# Repo smoke (brain must be running)
python scripts/smoke_web.py
```

## Lint (optional)

```bash
pip install ruff
ruff check backend scripts
```

Config: `ruff.toml` at repo root ([ISSUE-110](../docs/board/issues/ISSUE-110.md)).

## Tests (dev extras)

```bash
pip install -e ".[dev]"
# or: uv pip install -e ".[dev]"

pytest backend/tests
```

Add tests under `backend/tests/` ([ISSUE-115](../docs/board/issues/ISSUE-115.md)). Full dev OSS plan: [OSS_DEV_PLAN.md](../docs/dev/OSS_DEV_PLAN.md).

## Chat (streaming)

```bash
curl -N -X POST http://localhost:8787/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! What time is it?", "device_id": "test"}'
```
