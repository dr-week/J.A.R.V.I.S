# Development environment & scripts

**Plan sync:** [SYNC_PLAN.md](SYNC_PLAN.md) · [OSS_DEV_PLAN.md](OSS_DEV_PLAN.md) · [STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) · [PLAN_AUDIT.md](PLAN_AUDIT.md)

One place for **how to work fast** on Jarvis: scripts, OSS tools, daily commands, performance habits.

---

## Daily workflow (minimal)

```bash
# 1. Board + plan truth
python scripts/sync_workspace.py cursor   # or: devloop sync --owner YOU

# 2. Environment OK?
python scripts/check_dev_env.py

# 3. Brain (repo root — required for plugins/tools/)
python scripts/run_brain.py             # production-style
# OR dev reload:
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787 --reload

# 4. Primary UI (Vite — not Flutter for chat)
cd clients/web && npm run dev

# 5. Before devloop done
python scripts/verify_doc_links.py
```

**Windows one-shot:** `.\scripts\dev_up.ps1` — checks env, starts brain if port free, prints web command.

**Kill Windows UI orphans:** `clients\windows\kill_stale.ps1` before Flet `--pair`.

**Optional hooks:** `pip install pre-commit && pre-commit install` — doc links, dev env, and `ruff check backend/app backend/tests` on commit ([ISSUE-108](../board/issues/ISSUE-108.md)).

**GitHub CI:** `.github/workflows/dev-smoke.yml` runs on every push/PR to `main`/`master`: doc links, `check_dev_env.py`, `ruff check`, `pytest backend/tests`. No brain on port 8787 — `smoke_web.py` stays **local only** ([ISSUE-120](../board/issues/ISSUE-120.md)).

---

## Script map

| Script | Purpose | When |
|--------|---------|------|
| `devloop.py` | Board claim/done/sync/brief/inbox | Every agent session |
| `sync_workspace.py` | Alias `devloop sync [--owner]` | Session start |
| `run_brain.py` | Brain from **repo root** (correct imports) | Always-on / LAN |
| `check_dev_env.py` | Python, `.env`, brain import, optional node/flutter | Before coding |
| `verify_doc_links.py` | Broken relative links in key MD | Before `done` / PR |
| `smoke_web.py` | GET `/health` + `/sessions` | **Local** brain smoke — not in CI ([ISSUE-109](../board/issues/ISSUE-109.md)) |
| `helpers/issue_lane_verify.py` | Lane glob check | `devloop verify ISSUE-XXX` |
| `index_repo.py` | CODE_MAP generation | After large moves |
| `dev_up.ps1` | Win: env check + brain + hints | Human daily driver |
| `demo_up.ps1` / `demo_up.sh` | Presentation: brain + web + browser | [DEMO.md](../DEMO.md) |
| `helpers/repo_nav.py` | Find code (ISSUE-085) | Exploration |
| `helpers/board_copilot.py` | Suggest next issue (ISSUE-086) | Picking work |

### `devloop.py` essentials

```bash
python scripts/devloop.py sync --owner cursor
python scripts/devloop.py loop
python scripts/devloop.py claim ISSUE-115 --owner minimax2
python scripts/devloop.py verify ISSUE-115   # lane paths exist
python scripts/devloop.py done ISSUE-115          # warns on unchecked `- [ ]`
python scripts/devloop.py done ISSUE-115 --force  # override after verify
```

**Done gate:** unchecked markdown tasks in the issue body block `done` unless `--force` ([DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)).

---

## Open-source tools (integrate, don’t reinvent)

Locked defaults: [OSS.md](../OSS.md). **Recommended for dev velocity:**

| Tool | Area | Use in Jarvis | Status |
|------|------|---------------|--------|
| **FastAPI + Uvicorn** | Brain | Runtime | ✅ in use |
| **Vite + React + TS** | Web UI | Primary chat | ✅ in use |
| **Flutter SDK** | Field Body | Experimental | ✅ optional |
| **Ruff** | Python lint/format | Backend/plugins | ✅ CI + local `ruff check backend scripts` |
| **uv** | Python deps | Faster `pip install` | 🔲 optional; document in backend README |
| **Oxlint** (via Vite) | Web lint | `clients/web` | ✅ in template |
| **pre-commit** | Git hooks | `verify_doc_links` + `check_dev_env` | ✅ `.pre-commit-config.yaml` — `pip install pre-commit && pre-commit install` |
| **httpie** / `curl` | API smoke | `GET /health` | optional |
| **Flutter DevTools** | Field debug | WS bridge | when on 101 |

**Do not add** a second task runner (Make/just) until scripts grow — keep `devloop` + `dev_up.ps1` as entrypoints.

---

## Performance & efficiency rules

1. **One brain process** on `:8787` — check before start (`check_dev_env` / `dev_up`).
2. **One chat UI** — Vite only; don’t run Flet GUI + web for the same test.
3. **Repo-root uvicorn** — never `cd backend` only (breaks `tools.*` plugins).
4. **`devloop sync`** after issue changes — LIVE_PLAN is generated truth.
5. **`index_repo.py`** after moving modules — keeps [CODE_MAP.md](../CODE_MAP.md) useful for agents.
6. **Parallel workers** — max 2 NOW; use lanes ([PARALLEL.md](PARALLEL.md)).

---

## Planned script work (backlog)

| ID | Script / integration | Benefit |
|----|----------------------|---------|
| **108** | `pre-commit` config: links + `check_dev_env` | Catches doc drift early |
| **109** | `scripts/smoke_web.py` — health + sessions | FR-P3 CI-less smoke |
| **110** | `ruff` in backend README + `ruff.toml` | Faster Python feedback |
| **111** | `devloop verify ISSUE-XXX` — lane paths exist | Agent mistakes |

Mini-sized queue: [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md).

---

## Doc verify scope

`verify_doc_links.py` checks: README, AGENTS, `docs/dev/*.md`, plus plan cluster (`DESIGN`, `SYNC_PLAN`, `PRESENCE_STACKS`, `PLAN_AUDIT`).

---

## Related

[HOME_HUB.md](../HOME_HUB.md) · [SECURITY.md](../SECURITY.md) · [CODE_MAP.md](../CODE_MAP.md)
