# Modularity plan — manageable code for humans and AI coders

**Goal:** Small, named modules with clear imports so agents edit **one lane** without breaking the brain, clients, or factory scripts.

Related: [AI_CODE_STRUCTURE.md](AI_CODE_STRUCTURE.md) · [AI_CODER_AUTOMATION.md](AI_CODER_AUTOMATION.md) · [backend/app/README.md](../../backend/app/README.md) · board **117–118**, **122–124**, **103**, **115**

---

## 1. Principles

| Rule | Why |
|------|-----|
| **~200 lines max** per module (soft) | Fits small-context agents |
| **One concern per file** | Easier verify + review |
| **Facade for stable imports** | e.g. `soul.memory` re-exports stores |
| **Plugins at the edge** | `backend/plugins/*`, `tools/*` — not in `mind/` |
| **Clients are thin** | HTTP/WS only; policy lives in brain |
| **No business logic in `devloop.py`** | Board OS ≠ product runtime |

```text
         ┌─────────────┐
         │   clients   │  presentation + bridge only
         └──────┬──────┘
                │ HTTP / WS
         ┌──────▼──────┐
         │  api/       │  thin routers
         └──────┬──────┘
    ┌────────────┼────────────┐
    ▼            ▼            ▼
 mind/        soul/        hands/
    └────────────┼────────────┘
                ▼
         plugins/ + tools/
```

---

## 2. Current state (honest)

### Backend — mostly modular ✅

| Area | Status | Notes |
|------|--------|--------|
| Soul DB | ✅ | `soul/db.py` + `soul/stores/*` + `memory.py` facade |
| Hands | ✅ | `registry`, `gate`, `builtin_tools`, `plugin_loader` |
| Mind | ✅ | `agent.py` + `gemini_loop.py` |
| API | ✅ | One router per file; `chat.py` ~100 lines |
| Hotspots | 🔲 | `registry.py` ~178, `sync/manager.py` ~109, `learner.py` ~128 |

### Scripts — needs split 🔴

| File | Lines | Plan |
|------|-------|------|
| `devloop.py` | ~1150 | **117** core + **118** commands |
| Helpers | OK | `issue_lane_verify`, `board_copilot`, `repo_nav` |

### Web client — good start ✅

`api/` · `hooks/useJarvisApp` · `components/*` · `types/`

### Flutter — OK; cleanup 🔲

**103** remove `ui/chat/`; keep `field` + `data` + `state`

### Windows Flet — monolith 🔲

| File | Lines | Target |
|------|-------|--------|
| `client.py` | ~465 | `tray.py`, `ws_loop.py`, `cli.py` (future issue) |
| `ui_gui.py` | ~377 | stay or split per MINIMAX_UI waves |
| `voice.py` | ~215 | optional `stt.py` / `tts.py` later |

---

## 3. Phased roadmap

### Phase M0 — Rules (now)

- [x] [AI_CODE_STRUCTURE.md](AI_CODE_STRUCTURE.md) layer table
- [x] `devloop verify` + issue **Lane**
- [ ] **115** pytest — one test per package (`api`, `hands`, `soul`)
- [ ] **122** / **124** — `config.py` Settings + `logger.py` (no `core/` folder unless ADR)

**Exit:** New code follows layers; verify passes on claimed issues.

---

### Phase M1 — Factory scripts (**117 → 118**)

**Owner:** `minimax` (not mini — touches all commands)

```text
scripts/
├── devloop.py              # argparse + main() only (~150 lines)
├── core/
│   ├── board_io.py         # read/write issues, LIVE_PLAN, BACKLOG
│   ├── board_snapshot.py   # list_issues, rebuild, fingerprint
│   └── feedback_log.py     # feedback.jsonl (or import feedback.py)
├── commands/
│   ├── sync.py             # cmd_sync, cmd_refresh
│   ├── claim.py            # claim, release, done
│   └── comms.py            # say, inbox, loop, brief
├── agent_registry.py
└── helpers/                # unchanged
```

| Issue | Deliverable |
|-------|-------------|
| **117** | `scripts/core/*` — domain logic moved out of `devloop.py` |
| **118** | `scripts/commands/*` — all `cmd_*` handlers |

**Acceptance:** `python scripts/devloop.py sync` + full command smoke (manual checklist in issue).

---

### Phase M2 — Brain hardening

| Slice | Issue | Module change |
|-------|-------|----------------|
| Settings | **122** | `config.py` → pydantic `Settings`; `main.py` uses it |
| Logging | **124** | `logger.py`; replace startup prints |
| Tests | **115** | `backend/tests/test_health.py`, `test_gate.py` |
| Types | **116** | `api/*` only |
| Webhooks | **132** | Mount `api/webhooks.py` in `main.py`; broadcast via `sync.manager` |
| Optional split | new mini | `sync/ws_chat.py` vs `sync/device_bridge.py` if `manager.py` grows |

**Plugin rule:** New capabilities = new folder under `backend/plugins/<name>/` or `tools/<name>/`, never new top-level `app/` package without ADR.

---

### Phase M3 — Clients

| Slice | Issue | Outcome |
|-------|-------|---------|
| Flutter legacy | **103** | Delete chat default; Field-only `lib/` |
| Field confirm | **142** | `bridge_client` + `field_controller` only |
| Windows entry | *future* | Split `client.py` (document in MINIMAX_UI when touching Flet) |
| Web | — | Add `hooks/useSessions.ts` only if `useJarvisApp` grows again |

---

### Phase M4 — Product modularity (Phase 3+ ROADMAP)

| Piece | Pattern |
|-------|---------|
| Life domains | One plugin per domain (`reminders`, `tasks`, …) |
| Phase 6 SDK | `tools/` packages + schema in [TOOL_SCHEMA.md](../TOOL_SCHEMA.md) |
| Polyglot | **128** design → subprocess/Lua per [POLYGLOT_TOOLS.md](POLYGLOT_TOOLS.md) |
| Venture | Stay in `AI-COMPANY/`, not merged into `backend/app/main.py` |

---

## 4. Module ownership map (who edits what)

| Module | Agent lane | Do not edit without issue |
|--------|------------|---------------------------|
| `backend/app/api/` | cursor / API issues | — |
| `backend/app/mind/` | cursor | persona text in `soul/persona` |
| `backend/app/soul/stores/` | mini slices per store file | schema without `db.py` |
| `backend/app/hands/gate.py` | cursor + security review | casual changes |
| `backend/plugins/*` | minimax vertical | core gate |
| `clients/web/` | antigravity | backend |
| `clients/flutter/lib/` | minimax Field | web |
| `scripts/core/` | minimax **117** | product code |
| `docs/board/issues/` | devloop only | — |

---

## 5. Manageability checklist (every PR / `done`)

```bash
python scripts/devloop.py verify ISSUE-XXX
ruff check backend scripts
pytest backend/tests          # when 115 lands
python scripts/verify_doc_links.py   # if docs touched
```

- [ ] Diff stays inside issue **Lane**
- [ ] No new circular imports (`api` → `mind` → `hands` → `api` forbidden)
- [ ] Public import paths stable (`soul.memory`, `hands.registry`)
- [ ] [CODE_MAP.md](../CODE_MAP.md) refreshed if new top-level modules: `python scripts/index_repo.py map`

---

## 6. What we will not do (anti-modularity)

- Microservices / multiple brains — one FastAPI app until ADR
- `backend/app/core/` package **unless** **122** explicitly creates it (prefer extend `config.py`)
- Splitting `devloop` before **115** has at least smoke tests (recommended order: **115** → **117** → **118**)
- Duplicating confirm/policy in Flutter or web

---

## 7. Suggested execution order (next 4 weeks)

| Week | Focus | Issues |
|------|--------|--------|
| 1 | Close Field epic + tests dir | **101** done, **115** |
| 2 | Config + logging | **122**, **124** |
| 3 | Devloop core extract | **117** |
| 4 | Devloop commands + CI | **118**, **120** |

Parallel (second slot): **142** or **107** — product, not factory.

---

## 8. Success metrics

| Metric | Target |
|--------|--------|
| `devloop.py` size | &lt; 250 lines after **118** |
| Backend modules &gt; 200 lines | ≤ 3 files (exceptions documented) |
| `devloop verify` on all active issues | pass |
| pytest | health + gate + one API test |
| Agent mispicks wrong folder | down (lane + scope diff when built) |

---

## Related board issues

| ID | Title |
|----|--------|
| 115 | Pytest integration |
| 116 | Mypy API |
| 117 | Devloop core extraction |
| 118 | Devloop command extraction |
| 122 | pydantic-settings |
| 124 | loguru |
| 103 | Flutter strip chat |
| 142 | Field confirm |

Also: uncommitted work split → [PR_SPLIT.md](PR_SPLIT.md).

Update this doc when **117/118** change the target tree.
