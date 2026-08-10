# Lab stack — OSS catalog, Stark doctrine, phased actions

**Tone:** [VISION.md](../VISION.md) Iron Man intent — **trusted operator, local power, ship upgrades in slices**, not cosplay.

**Execution:** [OSS_DEV_PLAN.md](OSS_DEV_PLAN.md) · [STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) · [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md)

---

## What Tony Stark would do (engineering, not movies)

| Stark habit | Jarvis equivalent | Anti-pattern |
|-------------|-------------------|--------------|
| **One arc reactor** — power you own | Local brain + SQLite; keys in `.env` | Cloud-only brain lock-in |
| **Workshop first** — prototype fast, then armor | `devloop` + vertical slices + smoke tests | 3-month rewrite |
| **Friday runs the house** while you build | Web chat + Windows tray; Field executes | You babysitting two chat apps |
| **Instrument the suit** | action_log, health, **125** vitals, loguru | `print()` in production paths |
| **Upgrade in levels** | [FUTURE.md](../FUTURE.md) L0–L7, phase gate | Celery + wake word before Hands exit |
| **Open the garage** | OSS + HA + documented plugins | Secret sauce monolith |
| **Confirm before the missile** | `hands/gate.py`, **104** backend + **142** Field | Silent destructive tools |

**Stark would not:** add Redis/Celery because it sounds cool; duplicate JARVIS UI on every device; skip tests on the reactor.

---

## OSS catalog — integrate by phase (expanded)

### D1 — Dev factory (now)

| Tool | Role | Issue / action |
|------|------|----------------|
| pytest, mypy, ruff, pre-commit, uv | Quality | 119 ✅, **115**, **116**, 108–110 |
| **httpx** | Test client | in deps; use in **115** |
| **GitHub Actions** | Doc/env CI | **120** |
| **editorconfig** | Optional | future 1-file doc issue |

### Phase 2 tail — harden Hands

| Tool | Role | Issue |
|------|------|--------|
| **pydantic-settings** | Typed `.env` | **130** deps → **122** wire |
| **loguru** | Structured logs | **131** deps → **124** wire |
| **lupa** | Lua tool bodies | **129** after **128** |
| **psutil** | Host vitals tool | **125** (mini: dep + one tool) |
| **structlog** | Alt to loguru | skip unless ADR — pick one |

### Phase 3 — Life + memory

| Tool | Role | Issue / note |
|------|------|----------------|
| **sqlite-vec** | Embeddings in SQLite | new plugin issue |
| **Chroma** | Fallback vector DB | OSS.md |
| **alembic** | Schema migrations | **123** (main minimax, not first week) |
| **APScheduler** | Cron without Celery | prefer before **127** for simple jobs |
| **icalendar** / **caldav** | Calendar connectors | Phase 3 plugin |
| **feedparser** | RSS/web hooks | plugin |

### Phase 4 — Voice + ambient

| Tool | Role | Issue |
|------|------|--------|
| **faster-whisper** / **whisper.cpp** | Local STT | OSS.md |
| **Piper** | Local TTS | OSS.md |
| **openwakeword** | Wake word | **126** — phase **4**, not phase 0 |
| **webrtcvad** | Voice activity | optional slice |

### Phase 5 — House

| Tool | Role |
|------|------|
| **Home Assistant** REST/WebSocket | ✅ plugin path |
| **MQTT** (paho) | Room satellites later |
| **esphome** | DIY nodes — docs only until house lane |

### Phase 6 — SDK + scale (only if needed)

| Tool | Role | Gate |
|------|------|------|
| **Celery** + **Redis** | Heavy async queue | **127** — **after** Phase 3 exit + ADR |
| **OpenTelemetry** | Traces | when multi-host |
| **Sentry** (OSS self-host or SaaS) | Crash reports | optional |

---

## Script plan (waves A–Z)

| Wave | Name | Contents |
|------|------|----------|
| **U** | Velocity | ✅ smoke, verify, ruff, hooks |
| **X** | Tests | 119 ✅ → **115** → **116** → **120** |
| **Y** | Config + logs | **128** → **122** · **129** → **124** |
| **Z** | Suit sensors | **125** vitals · **126** wake (Phase 4) · **127** queue (gated) |
| **AA** | Future | `run_tests.ps1`, `scripts/bench_brain.py` (TBD) |

---

## MiniMax — phased actions (copy order)

```bash
python scripts/devloop.py next --owner minimax2 --tier mini
python scripts/devloop.py verify ISSUE-XXX
python scripts/devloop.py claim ISSUE-XXX --owner minimax2
```

### Phase A — tests (Wave X)

| # | Issue | Action | Files |
|---|-------|--------|-------|
| A1 | ~~119~~ | Add pytest deps | ✅ done |
| A2 | **115** | One `test_health.py` | `backend/tests/` |
| A3 | **116** | Fix types in one router | `backend/app/api/health.py` only |

### Phase B — config & logs (Wave Y)

| # | Issue | Action | Files |
|---|-------|--------|-------|
| B1 | ~~deps~~ | `pydantic-settings` / `loguru` in pyproject | ✅ |
| B2 | **122** | `Settings` + wire `main.py` | `backend/app/config.py` |
| B3 | **124** | `logger.py` + startup logs | `backend/app/logger.py` |

### Phase C — “suit vitals” (Wave Z, still mini)

| # | Issue | Action | Files |
|---|-------|--------|-------|
| C1 | **125** | `psutil` dep + `system_vitals` tool | `tools/` or hands plugin one file |

### Phase D — product (standard agent)

| # | Issue | Who |
|---|-------|-----|
| D1 | **142** Field confirm WS | cursor / minimax |
| D2 | **107** WS auth | cursor |
| D3 | **101** close | minimax |

**Do not assign mini:** **123** alembic, **117–118** devloop, **127** celery, **126** until Phase 4.

---

## Further ahead (12–24 months)

```text
2026 H2   Phase 2 exit → Phase 3 plugins (tasks, calendar, memory search)
2027 H1   Voice lane (Whisper/Piper) + PWA as default desktop
2027 H2   House hub (HA scenes) + room presence sketch
2028+     SDK for your robots; optional Celery only if single-process Mind bottlenecks
```

**North star unchanged:** one mind, many bodies, execute under your authority ([PARTNERSHIP.md](../PARTNERSHIP.md)).

---

## When adding any OSS

1. Phase gate in issue `blocked_by` or phase field.
2. One vertical slice; `starter` label if ≤2 files.
3. Update [OSS.md](../OSS.md) or this file.
4. ADR in [DECISIONS.md](../DECISIONS.md) if it replaces a locked default.

---

## Related

[FUTURE.md](../FUTURE.md) · [ROADMAP.md](../ROADMAP.md) · [PERSONA.md](../PERSONA.md)
