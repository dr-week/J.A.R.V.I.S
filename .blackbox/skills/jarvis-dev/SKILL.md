---
name: jarvis-dev
description: Develop Jarvis using docs/board and scripts/devloop.py. Use for issue-driven implementation (Blackbox MiniMax).
---

# Jarvis development — MiniMax (Blackbox)

**Canonical rules:** [docs/dev/MINIMAX.md](../../docs/dev/MINIMAX.md)  
**Doc map:** [docs/DOCS_MAP.md](../../docs/DOCS_MAP.md)  
**Also read:** [AGENTS.md](../../AGENTS.md) · [skills/jarvis-dev/SKILL.md](../../skills/jarvis-dev/SKILL.md)

**Owner id:** `minimax` (required on every devloop command)

---

## Session loop

```bash
python scripts/devloop.py sync --owner minimax
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner minimax
python scripts/devloop.py next --owner minimax
python scripts/devloop.py claim ISSUE-XXX --owner minimax
python scripts/devloop.py brief --owner minimax
```

---

## Hard rules (summary)

| Rule | Detail |
|------|--------|
| One issue | No second NOW claim; no scope creep |
| Claim first | Never code before `claim --owner minimax` |
| Lanes | Windows issues → `clients/windows/**` only; Android → `clients/android/**` only |
| Registry | Only `backend/app/hands/registry.py` — no duplicate tool systems |
| Client tools | `executor: "client"` + WS per [SYNC_PROTOCOL.md](../../docs/SYNC_PROTOCOL.md) |
| Verify | `py_compile`; bridge smoke test when issue touches device bridge |
| Done | All acceptance true → `update` → `done` → `say`- Append ADRs to `docs/DECISIONS.md` for architecture choices
- **Zero-Code OSS Rule:** Prefer 3-line PyPI wrappers, CLI subprocesses, Docker sidecars, or MCP servers over custom Python/JS implementations (see `docs/OSS.md`).
- **Backend OSS lane:** Read `docs/dev/BACKEND_OSS_PLAN.md`; keep adapters isolated, optional infrastructure behind extras, and add a contract test plus the OSS gate.
- **Chained verification:** Run `python scripts/verify_backend.py` before handoff.
- **Release verification:** Run `python scripts/verify_backend.py --full` before release.
- Never commit secrets |
| Parallel | Max 2 workers; do not edit other owner's claimed paths |
| Refactors | Forbidden unless issue requests |

---

## Pattern: device bridge (copy ISSUE-032)

1. Tool in `hands/registry.py` (`windows_open` / `android_open`, etc.)
2. `run_tool` → `_dispatch_to_device` → sync `request`/`resolve`
3. Client WS: `register` → handle `tool_execute` → `tool_result` with same `request_id`
4. Local executor module (e.g. `device_bridge.py` or Kotlin equivalent)
5. Update `SYNC_PROTOCOL.md` + client README

**Windows reference:** `clients/windows/client.py --bridge`, `device_bridge.py`  
**Do not use** httpx for WebSocket on Windows — use `websockets` package.

---

## Definition of done

See [docs/dev/DEFINITION_OF_DONE.md](../../docs/dev/DEFINITION_OF_DONE.md).

---

## Finish

```bash
python scripts/devloop.py update ISSUE-XXX --note "shipped + verified"
python scripts/devloop.py done ISSUE-XXX
python scripts/devloop.py say --from minimax --to cursor --kind done --issue ISSUE-XXX -- "summary"
```

---

## Current assignment

Run `python scripts/devloop.py next --owner minimax` — expected **ISSUE-033** (Android bridge, mirror 032).

---

## Product

[docs/PERSONA.md](../../docs/PERSONA.md) · [docs/SCOPE.md](../../docs/SCOPE.md) · [docs/PARTNERSHIP.md](../../docs/PARTNERSHIP.md)

Do not weaken confirmation gates. Execute > explain.
