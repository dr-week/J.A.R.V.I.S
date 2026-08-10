# Strategy

**Doc sync:** [DOCS_MAP.md](DOCS_MAP.md) · **Presence + board sync:** [dev/SYNC_PLAN.md](dev/SYNC_PLAN.md)

## How we win

1. **Spec the operator platform** (done in D0 docs)
2. **Automate the build loop** so Cursor + Antigravity / Claude keep shipping (D1)
3. **One brain + focused bodies** — web = chat; Flutter = Field; Windows = agent (ADR-0023)
4. **Make it personal** (Phase 1 Soul)
5. **Make it execute** (Phase 2 Hands)
6. **Add life domains as plugins** (Phase 3)
7. **Make it ambient** (Phase 4 voice, Phase 5 house)
8. **Make it endlessly expandable** (Phase 6 SDK)

North star: [FUTURE.md](FUTURE.md) · Forward plan: [dev/STRATEGY_FORWARD.md](dev/STRATEGY_FORWARD.md) · Co-labor: [PARTNERSHIP.md](PARTNERSHIP.md)

## Presence strategy (no duplicate chat apps)

| Body | Stack | Job |
|------|-------|-----|
| Web | Vite + TypeScript | Chat, sessions, settings, design |
| Flutter | Dart | Field Body — bridge, client tools, confirmations |
| Windows | Flet + Python | Tray, voice, bridge — not product chat UI |

Full rules: [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md) · [dev/FLUTTER_FIELD.md](dev/FLUTTER_FIELD.md)

## Phase division (cheat sheet)

| Phase | Theme | Deliverable |
|-------|-------|-------------|
| D0–D1 | Docs + devloop | Done |
| 0–6 issue backlog | Per ROADMAP | **54+ issues done**; new work via SYNC_PLAN queue |
| Next product slice | Web sessions ✅ (102); Field UI ✅ (112–114); close **101**; **142** Field confirm |

## Where we are now (refresh after `devloop sync`)

| Area | Status |
|------|--------|
| Board | **101** NOW; open **103**, **106–107**, **115–118**, **142** — [LIVE_PLAN.md](board/LIVE_PLAN.md) |
| Chat + sessions | **Web** — 102 done |
| Flutter Field | UI shipped; **101** + **103** cleanup remain |
| Dev quality | Wave U done; Wave X **115–116** queued |
| Brain | repo-root uvicorn · `smoke_web.py` |

## Next concrete actions

```bash
python scripts/devloop.py sync
python scripts/devloop.py loop
```

| Priority | Issue | Suggested owner |
|----------|-------|-----------------|
| In flight | **101** Flutter Field epic | minimax |
| Next NOW | **115** pytest or **107** WS auth | cursor / minimax2 |
| Mini parallel | **115** pytest, **116** mypy | minimax2 (`next --tier mini`) |
| After 101 | **103** strip Flutter chat | minimax |

**Quality / later:** ISSUE-106 PWA, ISSUE-107 WS auth, **108** pre-commit, pairing hardening.

## 🚀 Future Strategy (Phase 3+ & Dev Env)

### 1. Dev Environment Scale-Up
- **CI/CD Integration:** We will introduce GitHub Actions to enforce `pytest`, `ruff`, and `mypy` on all pull requests. This is crucial as the multi-agent swarm (Cursor, Antigravity, Minimax) scales.
- **Containerization:** A `Dockerfile` will be added to ensure the Jarvis brain can run identically on any host (VPS, Raspberry Pi, Home Hub).

### 2. Product Integrations (OSS-First)
- **Phase 3 (Life Tools):** We will leverage established Python OSS libraries (e.g. `google-auth` for calendar, standard CalDAV for tasks) wrapped in standardized plugins.
- **Phase 4 (Voice):** Ambient presence will utilize lightweight, local OSS models: **Whisper.cpp** for Speech-to-Text and **Piper TTS** for Text-to-Speech to guarantee privacy and low latency.
- **Phase 5 (House):** Jarvis will act as the "brain", using the existing Home Assistant REST/WS API as its "hands" for environmental control, rather than reinventing smart home protocols.

### 3. Agent Swarm Orchestration
As parallel work scales, `devloop.py` will evolve to include an **Orchestrator Role**. This will automatically analyze incoming issues and route them to the most capable agent seat (`minimax` for isolated scripts, `antigravity` for UI slices, `cursor` for backend architecture) to minimize manual assignment.

## Parallelism — 2 workers

- NOW capacity = **2** · `--owner` on every claim
- Lanes: [dev/PARALLEL.md](dev/PARALLEL.md) · [dev/SYNC_PLAN.md](dev/SYNC_PLAN.md) §4

| When | Worker A | Worker B |
|------|----------|----------|
| Product UI | `antigravity` → `clients/web/**` | `cursor` → `backend/**` |
| Field Body | `minimax` → `clients/flutter/**` (101) | `cursor` → **142** Field confirm, **107** WS auth |
| Windows integration | `minimax` → `clients/windows/**` bridge/voice | Web or backend (other tree) |

**Never:** parallel chat UI in Flutter and web for the same acceptance.

## Agent routing

| Agent | Owner id | Best use |
|-------|----------|----------|
| Cursor | `cursor` | Backend, review, sync docs, architecture |
| Antigravity | `antigravity` | Web product UI, vertical slices |
| MiniMax | `minimax` | Bridge, plugins, Flutter Field |
| MiniMax 2 | `minimax2` | **115–116**, **106**, helpers (`next --tier mini`) |
| Claude | `claude` | Parallel seat |

MiniMax: [dev/MINIMAX.md](dev/MINIMAX.md) · [.blackbox/RULES.md](../.blackbox/RULES.md)

Full audit: [dev/PLAN_AUDIT.md](dev/PLAN_AUDIT.md)
