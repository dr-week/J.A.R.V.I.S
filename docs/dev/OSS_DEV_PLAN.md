# Open-source dev plan — tools, scripts, mini issues

**Product OSS (runtime):** [OSS.md](../OSS.md) · **Horizons:** [STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) · **Queue:** [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md)

**Upstream repository inventory:** [GITHUB_INTEGRATIONS.md](../GITHUB_INTEGRATIONS.md).
Update the inventory and this plan together when an integration changes status.

## Proposed next integration wave

Implement one item at a time, in this order:

| Order | Repository | Scope | Acceptance proof |
|---|---|---|---|
| 1 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | Optional model gateway and token/cost metadata | Gemini plus one OpenAI-compatible/local endpoint; secrets stay brain-local |
| 2 | [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector) | Brain, agent loop, tools, confirmations, and bridge traces | End-to-end trace exists; telemetry outage does not break chat |
| 3 | [searxng/searxng](https://github.com/searxng/searxng) | Optional private backend for web research | Local/mocked search passes with timeout, size, and secret-redaction checks |

Every wave requires: a small issue, `.env.example` updates if configuration
is added, focused tests, documentation links, and a rollback path. Do not
mark a repository **In use** until the acceptance proof passes.

Small-chunk rule: split each repository into three slices and keep them in the
same order everywhere.

1. Contract and config shape.
2. Runtime wiring.
3. Acceptance proof plus docs sync.

One table for **what to integrate**, **which script/issue owns it**, and **how small to slice** for MiniMax.

---

## 1. Dev & quality OSS (integrate now)

| Tool | Why | Repo touch | Script / habit | Issue | Mini? |
|------|-----|------------|----------------|-------|-------|
| **FastAPI + Uvicorn** | Brain API | `backend/` | `run_brain.py` | — | ✅ in use |
| **Ruff** | Lint + format | `pyproject.toml`, `ruff.toml` | `ruff check backend scripts` | 110 ✅ | yes |
| **pre-commit** | Gate bad commits | `.pre-commit-config.yaml` | `pre-commit install` | 108 ✅ | yes |
| **pytest** + **pytest-asyncio** | Replace scratch tests | `pyproject.toml`, `backend/tests/` | `pytest backend/tests` | **119** ✅ → **115** | mini |
| **mypy** | API type safety | `pyproject.toml`, `backend/app/api/` | `mypy backend/app/api` | **116** | yes (api only) |
| **uv** | Fast install/run | docs + optional CI | `uv run pytest` | 115 acceptance | doc slice |
| **httpx** | Brain HTTP tests | already in `pyproject` deps | use in tests | 115 | — |
| **Vite + Oxlint** | Web UI | `clients/web` | `npm run dev` / `lint` | — | ✅ |
| **Flutter SDK** | Field Body | `clients/flutter` | `flutter analyze` | 101/103 | main minimax |

**Do not add:** Make, just, tox, poetry (unless ADR) — keep `devloop` + `dev_up.ps1` as entrypoints.

---

## 2. Product OSS (integrate by phase)

| Phase | Tool | Jarvis use | Issue / when |
|-------|------|------------|--------------|
| 3 | **sqlite-vec** / Chroma | Semantic memory | Phase 3 plugin |
| 3 | **APScheduler** | Cron jobs | Before Celery — see **127** ADR |
| 3 | **alembic** | Migrations | **123** (main agent) |
| 3 | **pydantic-settings** | Config | **119** ✅ → **122** |
| 2 | **loguru** | Logs | pyproject ✅ → **124** |
| 6 | **lupa** | Lua plugins | **129** after **128** |
| 2 | **psutil** | Host vitals tool | **125** |
| 4 | **Whisper** / faster-whisper | STT | Phase 4 |
| 4 | **Piper** | TTS | Phase 4 |
| 4 | **openwakeword** | Wake prototype | **126** |
| 5 | **Home Assistant** | House fabric | plugin |
| 6 | **Celery**+Redis | Heavy queue | **127** ADR only |

---

## 3. Script roadmap (waves)

| Wave | Goal | Status | MiniMax owner |
|------|------|--------|---------------|
| **U** | Daily velocity | ✅ smoke_web, verify, ruff, pre-commit | minimax2 (done) |
| **X** | Test + types | 119 ✅, **115**, **116**, **120** | **minimax2** |
| **Y** | Config + logs | **122**, **124** (deps in pyproject) | **minimax2** |
| **Z** | Vitals + voice (gated) | **125**, **126** (Ph4), **127** ADR | mixed |

**Stark doctrine + full OSS catalog:** [LAB_STACK.md](LAB_STACK.md).

### Planned scripts (not built yet)

| Script / workflow | Purpose | Issue |
|-------------------|---------|-------|
| `scripts/run_tests.ps1` / `.sh` | `pytest` + exit code for humans | part of **115** |
| GitHub Action `dev-smoke` | `check_dev_env` + `verify_doc_links` + `smoke_web` | **120** (optional) |

---

## 4. MiniMax micro-slices (copy-paste order)

**Rule:** `python scripts/devloop.py next --owner minimax2 --tier mini` then `verify` then `claim`.

| Step | Issue | Files only | Time box |
|------|-------|------------|----------|
| 1 | ~~**119**~~ | pytest deps | ✅ |
| 2 | **115** | `backend/tests/test_brain.py` | ~30 min |
| 3 | **116** | `backend/app/api/*.py` types | ~45 min |
| 4 | **122** | Settings in `config.py` (after **119**) | ~30 min |
| 5 | **124** | `logger.py` | ~30 min |
| 6 | **125** | psutil vitals tool | ~30 min |
| 7 | **106** | PWA web | ~30 min |

**Velocity (standard tier, not mini):** **130** → **131** → **132**.

**Standard (needs NOW slot or deep context):** **107** WS auth, **142** Field confirm, **117–118** devloop refactor.

---

## 5. Future strategy (summary)

```text
NOW     101 done + 104 (backend) + 142 (Field)  →  Phase 2 exit
NEXT    103 · 107 · 106          →  harden + PWA
THEN    Phase 3 life plugins     →  sqlite-vec, tasks connectors
LATER   Voice / House / SDK      →  OSS.md phase table
```

Full narrative: [STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) · [FUTURE.md](../FUTURE.md).

---

## 6. After integrating a tool

1. Add to [OSS.md](../OSS.md) or this file if dev-only.
2. One line in [DEV_ENV.md](DEV_ENV.md) script map.
3. Optional: `pre-commit` local hook (only if fast).
4. `devloop done` + `sync` — do not leave docs stale.

---

## Related

[DEV_ENV.md](DEV_ENV.md) · [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md) · [PROCESS.md](PROCESS.md)
