# Backend app package — map for coding agents

Run brain from **repo root** so `tools/` and `backend.plugins` resolve:

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787 --reload
```

## Layout

```text
backend/app/
├── main.py           # FastAPI app, routers, lifespan (init_db + discover_plugins)
├── config.py         # Env → settings; llm_ready()
├── api/              # HTTP routers only — thin, call soul/mind/hands
├── mind/
│   ├── agent.py      # stream_chat orchestration
│   └── gemini_loop.py # Gemini tool loop (edit LLM provider here)
├── soul/
│   ├── db.py         # SQLite connection + schema + init_db()
│   ├── memory.py     # Stable import facade (re-exports stores)
│   ├── stores/       # One file per table group — edit the smallest file
│   ├── persona.py    # System prompt + profile
│   ├── learner.py    # observe() after each turn
│   └── tools.py      # LLM-facing memory tools
├── hands/
│   ├── registry.py   # register(), run_tool(), REGISTRY
│   ├── gate.py       # Confirmation + allowlist
│   ├── builtin_tools.py  # hello_world, device open tools
│   └── plugin_loader.py  # backend/plugins + tools/
├── sync/
│   └── manager.py    # WebSocket devices, tool_execute bridge
└── company/          # Venture stubs (Phase 8+)
```

## Where to edit (common tasks)

| Task | File(s) |
|------|---------|
| New HTTP route | `api/<area>.py` + register in `main.py` |
| New brain tool | `backend/plugins/<name>/` or `tools/<name>/` |
| Tool safety / confirm | `hands/gate.py` |
| Chat turn flow | `mind/agent.py` |
| Gemini behavior | `mind/gemini_loop.py` |
| DB schema | `soul/db.py` + matching `soul/stores/*.py` |
| Persona text | `soul/persona.py`, `docs/PERSONA.md` |

## Import rule

Prefer `from backend.app.soul.memory import …` in plugins; inside `backend/app` use relative imports (`from ..soul.memory import …`).

**Do not** import `tools` from `backend/` cwd only — start uvicorn from repo root.

See also: [docs/dev/AI_CODE_STRUCTURE.md](../../docs/dev/AI_CODE_STRUCTURE.md)
