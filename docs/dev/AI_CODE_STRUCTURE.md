# AI-friendly code structure

How this repo is organized so **small-context agents** (MiniMax, fast passes) can find the right file quickly and avoid breaking unrelated layers.

Related: [AGENTS.md](../../AGENTS.md) coding style · [CODE_MAP.md](../CODE_MAP.md) · [MODULARITY_PLAN.md](MODULARITY_PLAN.md) · [backend/app/README.md](../../backend/app/README.md)

---

## Repo spine

```text
jarvis/
├── backend/app/     # Brain — Soul + Mind + Hands + API
├── backend/plugins/ # Optional connectors (weather, HA, …)
├── tools/           # Repo-root tool packages (loaded at startup)
├── clients/
│   ├── web/         # Primary chat UI (Vite + React)
│   ├── flutter/     # Field Body (bridge, confirm) — not primary chat
│   ├── windows/     # Flet tray + device_bridge.py
│   └── android/     # Kotlin bridge
├── docs/            # Product truth + board
├── scripts/         # devloop, smoke, verify
└── eval/            # Benchmark cases (self-improvement loop)
```

---

## Layer rules (do not mix)

| Layer | May import | Must not |
|-------|------------|----------|
| `api/*` | soul, mind, hands, sync | Heavy LLM logic inline |
| `mind/*` | soul, hands, config | SQL directly |
| `soul/stores/*` | `soul/db.py` only | FastAPI, registry |
| `hands/registry.py` | soul (audit), gate, sync | Persona prompts |
| `clients/*` | HTTP/WS to brain | Duplicate business rules |

---

## File size guidance

Target **&lt; 200 lines** per module for agent edits. When a file grows:

1. Split by **concern** (already done: `soul/stores/*`, `hands/builtin_tools.py`, `mind/gemini_loop.py`).
2. Keep a **facade** (`soul/memory.py`) so callers do not churn.
3. One router per `api/*.py` file.

---

## Clients — where to edit

### Web (`clients/web/src/`)

```text
api/           brainApi.ts, syncSocket.ts — HTTP/WS only
hooks/         useJarvisApp.ts — state + side effects
components/    UI pieces (ChatView, AppSidebar, Settings)
types/         Shared TS types
App.tsx        Layout shell only
```

### Flutter Field (`clients/flutter/lib/`)

```text
app/           jarvis_app.dart — MaterialApp + routes
ui/field/      Field screen (default body)
ui/chat/       Legacy — remove when ISSUE-103 done
data/          bridge_client, brain_api
state/         field_controller, chat_controller
core/          theme, config, token_store
```

### Windows (`clients/windows/`)

- `client.py` — entry, tray, WS loop  
- `device_bridge.py` — `tool_execute` for windows_open  
- `ui_gui.py` — Flet UI (maintenance)

---

## Verification before `devloop done`

```bash
ruff check backend scripts
pytest backend/tests
python scripts/smoke_web.py
python scripts/verify_doc_links.py
```

---

## Self-improvement edits

Controlled code mutation: [SELF_IMPROVEMENT_LOOP.md](SELF_IMPROVEMENT_LOOP.md). Prefer `experiment/*` branches and update [SELF_STATE.md](SELF_STATE.md) after eval.
