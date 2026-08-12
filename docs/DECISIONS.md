# Decisions (ADR log)

Append-only. Newest at top.

## ADR-0026 — Background queue (APScheduler vs Celery)

- **Date:** 2026-08-11
- **Decision:** Use **APScheduler** (in-process) for background tasks and cron jobs. Reject **Celery + Redis** for the current architecture.
- **Why:** The "Stark doctrine" (defined in `LAB_STACK.md`) prioritizes a single, self-contained run model ("One arc reactor") for the home hub. Celery + Redis introduces unnecessary infrastructure complexity, external dependencies, and deployment overhead for a single-user personal AI. An in-process scheduler (APScheduler) is sufficient for background cron tasks, polling, and reminders without requiring external message brokers.
- **Follow-up:** Implement APScheduler for Phase 3 background tasks. Re-evaluate Celery only in Phase 6+ if the single-process `Mind` severely bottlenecks. Close ISSUE-127.

## ADR-0025 — Polyglot tool executor interface (subprocess-first)

- **Date:** 2026-08-11
- **Decision:** Implement polyglot tools starting with a subprocess runner. Tools can be written in Go, R, Rust, or any binary, communicating via stdin/stdout JSON. The `runtime` schema field dictates execution (`python`, `lua`, or `subprocess`). Embedded Lua is next (ISSUE-129), while gRPC, MATLAB, and rpy2 are deferred.
- **Why:** Keeps the core brain (Python) stable while allowing tools in other languages. Subprocess provides strong isolation and a clear boundary for non-Python tools.
- **Doc:** [dev/POLYGLOT_TOOLS.md](dev/POLYGLOT_TOOLS.md), [TOOL_SCHEMA.md](TOOL_SCHEMA.md)
- **Follow-up:** Implement Lua embedded execution in ISSUE-129.

## ADR-0024 — Mutator vs evaluator (controlled self-improvement)

- **Date:** 2026-08-10
- **Decision:** Jarvis may propose self-changes (prompts, config, code) only through scoped **mutators** on **`experiment/*` git branches**. **Promotion** requires an independent **evaluator** (pytest, smoke, `eval/` harness, human merge) — the same agent that authored the mutation must not be the sole judge of fitness.
- **Why:** FRIDAY-style evolution without production hot-patch or self-deleting safety rails.
- **Doc:** [dev/SELF_IMPROVEMENT_LOOP.md](dev/SELF_IMPROVEMENT_LOOP.md), [eval/README.md](../eval/README.md).
- **Follow-up:** `scripts/run_eval.py` when ISSUE-115+ lands; populate `eval/` cases per phase.

## ADR-0023 — Presence stack roles (Vite primary, Flutter experimental, Flet legacy)

- **Date:** 2026-08-09
- **Decision:** Three folders under `clients/`, but **one chat product** in `clients/web/` (Vite + TypeScript). Flutter = optional spike, not parallel feature factory. Flet = Windows integration (tray/voice/bridge), GUI in maintenance-only.
- **Why:** Avoid agents mixing Dart and TypeScript in one “stack”; ship browser UI fast while Flutter proves parity.
- **Follow-up:** Implement Field Body per [FLUTTER_FIELD.md](dev/FLUTTER_FIELD.md); strip legacy chat UI from Flutter when Field screens ship.

## ADR-0020 - GitHub as the first non-Google connector (ISSUE-042)

- **Date:** 2026-08-08
- **Decision:** Add a brain-executed GitHub connector plugin under `backend/plugins/github/`. Its `github_issues_list` tool reads repository issues through the GitHub REST API.
- **Why:** GitHub is useful, non-Google work context and has a small, stable read-only first slice that proves the connector pattern without granting write access.
- **Credential boundary:** A fine-grained personal access token or OAuth access token is read only from `JARVIS_GITHUB_TOKEN` in the brain host's `.env`; it is never accepted in tool parameters, stored in client state, or returned/logged by the tool.
- **Follow-up:** Add explicit-confirmation write tools only after the OAuth authorization and token-rotation flow is designed.

## ADR-0019 — Home Assistant bridge for house Hands (ISSUE-061)

- **Date:** 2026-08-08
- **Decision:** Use **Home Assistant** as the house device fabric (matching [OSS.md](OSS.md) house default). The brain talks to HA over its REST API (`/api/...`) using a long-lived access token, exposed as two Jarvis tools in a plugin under `backend/plugins/homeassistant/`:
  - `home_entity_list` (risk `auto`) — read-only list of HA entities/states.
  - `home_entity_set` (risk `confirm_once`) — turn an entity (e.g. a light) on/off, optional brightness 0–255.
- **Why:** HA is the locked OSS default for Phase 5 house control; it lets Jarvis control any brand's devices through one fabric instead of per-brand drivers. REST is the lowest-friction, cross-platform bridge for v1 (WebSocket/events can come later).
- **Details:**
  - Config via env: `JARVIS_HA_URL`, `JARVIS_HA_TOKEN`, `JARVIS_HA_ENTITY` (default `light.living_room`).
  - Executor `house` per [TOOL_SCHEMA.md](TOOL_SCHEMA.md); tools run on the brain (house hub) and call HA directly.
  - If HA is unconfigured, tools fail visibly with a clear error — never silently pretend success.
  - `home_entity_set` enforces the confirmation gate (`confirm_once`, allowlisted per device) and is written to `action_log`.
- **Follow-up:** Add room scenes, presence, and HA event/WebSocket subscriptions in later Phase 5 issues; keep the same REST bridge pattern.

## ADR-0018 — Always-on home host run mode (ISSUE-060)

- **Date:** 2026-08-08
- **Decision:** The brain runs as an always-on service on the home hub: a production launcher (`scripts/run_brain.py`) starts uvicorn **without `--reload`**, binds `0.0.0.0` by default so LAN clients reach it, and is managed by the OS service manager (Linux `systemd` unit / Windows Task Scheduler "At startup") so it survives reboots. `GET /health` is the LAN liveness signal.
- **Why:** The house experience (Phase 5) requires the brain to stay awake and be reachable from a phone on the LAN; `--reload` and foreground dev runs do not survive reboots or reboots restarts.
- **Details:**
  - Run mode documented in [HOME_HUB.md](HOME_HUB.md): requirements, dev vs always-on modes, systemd + Task Scheduler service examples, remote `/health` check, firewall/procedure notes, troubleshooting.
  - `scripts/run_brain.py` reads `HOST`/`PORT` from `backend/app/config.py` and prints the LAN health-check URL on startup.
  - No change to the `/health` endpoint itself; it was already present since ISSUE-010.
- **Follow-up:** Phase 5 later issues add Home Assistant bridge, room presence, and scenes; keep the same service-managed run model.

## ADR-0017 — Cross-device memory sync with LWW v1 (ISSUE-022)

- **Date:** 2026-08-08
- **Decision:** Memory writes converge via Last-Write-Wins (v1): `upsert_memory` only overwrites when the incoming `updated_at` is strictly newer than the stored value; the brain remains the source of truth and broadcasts `push_memory` over WebSocket; clients mirror pushes into a local cache. Windows client stores the mirror at `~/.jarvis/windows_sync_cache.json`.
- **Why:** Two devices must see the same memory after a write, but CRDTs are out of scope for v1 (per SCOPE.md). LWW is the simplest correct policy; v2 may move to CRDTs.
- **Details:**
  - API `PUT /soul/memories/{key}` accepts an optional `updated_at` (client can send its fresher timestamp) and returns `applied` (True/False) so the client knows if its write won.
  - A `push_memory` with empty value signals a delete.
  - `/sync/status` now returns `active_devices` (fixes a stale `active_connections` reference).
- **Follow-up:** Android client should mirror pushes similarly; revisit CRDT v2 in a later phase.

## ADR-0017 — Internal helpers Wave 1 only

- **Date:** 2026-08-08
- **Decision:** Add script helpers under `scripts/helpers/` starting with Repo Navigator + Board Copilot; defer Doc/UI/Test/Summarizer until Wave 1 proves token savings. Spec: [INTERNAL_HELPERS.md](dev/INTERNAL_HELPERS.md)
- **Why:** Agents waste tokens on repeated search/board orientation; keep tooling narrow and read-only
- **Follow-up:** ISSUE-085, ISSUE-086; regenerate index via `index_repo.py` (084 done)

## ADR-0016 — Dynamic LIVE_PLAN / LIVE_BRIEF from board state

- **Date:** 2026-08-08
- **Decision:** `scripts/board_context.py` + `devloop sync|brief|plan` regenerate `docs/board/LIVE_PLAN.md` and `LIVE_BRIEF.md` with fingerprint, per-owner picks, lanes, and inbox — replacing static `prompt` output
- **Why:** Agents were getting identical instructions; board and plan must drive variable work packages each session
- **Follow-up:** Run `sync` after claim/done; agents read LIVE_BRIEF at session start

## ADR-0015 — Documentation map (sync hub)

- **Date:** 2026-08-08
- **Decision:** Maintain [DOCS_MAP.md](DOCS_MAP.md) as index for canonical vs mirror markdown (`skills/` ↔ `.blackbox/skills/`, MINIMAX ↔ RULES)
- **Why:** Vision, partnership, MiniMax rules, and skills were drifting; agents need one edit checklist
- **Follow-up:** When changing agent rules or north-star docs, run DOCS_MAP edit checklist

## ADR-0014 — Human–agent partnership model

- **Date:** 2026-08-08
- **Decision:** Document co-labor in [PARTNERSHIP.md](PARTNERSHIP.md): human owns judgment, secrets, and money risk; agents own issue-scoped implementation; Jarvis is shared productivity + platform asset
- **Why:** User intent is era of working together for a better future — needs explicit roles, not implied chat rapport
- **Follow-up:** Weekly priorities via `devloop say` or Soul memory; money-moving actions remain human-confirm always

## ADR-0013 — Client tool dispatch over WebSocket (ISSUE-032)

- **Date:** 2026-08-08
- **Decision:** Client-executor tools use `/ws` messages `register`, `tool_execute`, `tool_result` with `request_id` correlation via `ConnectionManager.request()` / `resolve()`
- **Why:** MiniMax delivered a working Windows bridge without polling; pattern reusable for Android (033)
- **Follow-up:** Document in [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md); require device online for client tools; ISSUE-013 for auth on WS

## ADR-0012 — Cross-agent feedback bus

- **Date:** 2026-08-08
- **Decision:** `docs/board/feedback.jsonl` + `FEEDBACK.md` with `devloop loop|inbox|say`; claim/done auto-post
- **Why:** Cursor and Antigravity need a shared loop without relying on humans re-pasting status
- **Follow-up:** Optional dashboard panel in `scripts/feedback.py` later

## ADR-0011 — Prefer open-source building blocks

- **Date:** 2026-08-07
- **Decision:** Lean on OSS for commodity capabilities; Jarvis owns integration (Soul/Mind/Hands). Defaults in [OSS.md](OSS.md): Whisper+Piper (voice), Home Assistant (house), sqlite-vec (semantic memory), Flet (Windows presence), Kotlin stub first for Android
- **Why:** Faster path to Iron Man / house AI without reinventing STT/TTS/IoT/search
- **Follow-up:** Phase issues should name the OSS dependency in acceptance when relevant

## ADR-0010 — Self-learning engine architecture

- **Date:** 2026-08-07
- **Decision:** Passive observer + pattern detector + habit store + proactive trigger engine; all data stays in brain SQLite
- **Why:** User intent is "learns by itself, habits, tracks" — this cannot be achieved with explicit memory alone
- **Follow-up:** Phase 1 baseline: time + topic patterns; Phase 2+: device/location context

## ADR-0009 — Configurable AI name via env/API

- **Date:** 2026-08-07
- **Decision:** `ASSISTANT_NAME` env var + `PATCH /config`; default is `Jarvis`; no code change for rename
- **Why:** User confirmed name may change; baking "Jarvis" into code would require refactoring
- **Follow-up:** Persona file and system prompt template use `{assistant_name}` placeholder

## ADR-0008 — Windows client: Python Textual TUI for Phase 0

- **Date:** 2026-08-07
- **Status:** **Superseded by [ADR-0021](#adr-0021--windows-client-evolved-to-flet-desktop-ui)** (2026-08-08). Do not implement new Windows UI in Textual.
- **Decision:** Use Python + Textual for the Phase 0 Windows client (rich terminal UI)
- **Why:** Same language as brain, fastest to ship, no Electron overhead; Tauri/Electron considered for Phase 4+ voice chrome
- **Follow-up:** Historical only. Active client: `clients/windows/` Flet GUI + CLI `--once`; see [MINIMAX_UI.md](dev/MINIMAX_UI.md).

## ADR-0022 — Flutter presence UI (portrait-first, adaptive landscape)

- **Date:** 2026-08-09
- **Decision:** New cross-platform presence shell in `clients/flutter/`: **portrait phone layout by default**; at width ≥600 logical px (typically landscape phone or wider), show a **side rail** + main chat column; at ≥840 use expanded split. Same brain APIs as Flet/Compose.
- **Why:** One UI codebase for phone + desktop; user asked for vertical phone UX that stays flexible in landscape.
- **Follow-up:** ISSUE-092 scaffold; ISSUE-093 brain wiring; deprecate Flet GUI only after Flutter chat slice ships. Kotlin Compose Android may coexist until bridge parity.

## ADR-0021 — Windows client evolved to Flet desktop UI

- **Date:** 2026-08-08
- **Decision:** The current Windows presence surface uses a Python/Flet desktop UI with tray support instead of the original Textual TUI.
- **Why:** The shipped client now provides a more direct desktop presence affordance while staying in the Python stack and keeping UI slices small enough for parallel work.
- **Follow-up:** Keep the old Textual ADR as historical context; future Windows UI issues should assume Flet unless an issue explicitly says otherwise.

## ADR-0007 — LLM provider: Gemini (OpenAI-compatible fallback)

- **Date:** 2026-08-07
- **Decision:** Google Gemini Flash 2.0 as default via `google-genai` SDK; OpenAI-compatible via env override
- **Why:** 1M context window enables full memory injection without chunking; Google ecosystem fits Android/home hub target
- **Follow-up:** Ollama local support planned for Phase 6

## ADR-0006 — Memory store: SQLite for v1

- **Date:** 2026-08-07
- **Decision:** SQLite (`data/brain.db`) for all Soul data: memories, habits, interaction_log, sessions, action_log
- **Why:** Zero infra, git-backupable, sufficient for single-user v1; migrate path to PostgreSQL if multi-user
- **Follow-up:** Add `sqlite-vec` extension in Phase 3 for semantic memory search

## ADR-0006 — Two parallel workers (people or AIs)

- **Date:** 2026-08-07
- **Decision:** NOW capacity = 2; mandatory `--owner` on claim/next/prompt; `release` + anti-steal locks
- **Why:** Two humans or two AIs develop simultaneously without colliding
- **Owners:** `cursor` (Cursor), `antigravity` (Google Antigravity), `claude` (Claude Sonnet when used)
- **Follow-up:** Lane pairs in `docs/dev/PARALLEL.md`

## ADR-0007 — Other AI seats: Antigravity + Claude Sonnet

- **Date:** 2026-08-07
- **Decision:** Treat Google Antigravity as the primary co-agent; Claude Sonnet as the alternate other-AI seat
- **Why:** User runs Antigravity often, Claude Sonnet sometimes, alongside Cursor
- **Follow-up:** Keep MiniMax/Blackbox optional; prompts stay owner-agnostic via `devloop prompt --owner`

## ADR-0005 — Markdown board as project DB (v1)

- **Date:** 2026-08-07
- **Decision:** Use `docs/board/*.md` + issue files as the task database
- **Why:** Git-friendly, agent-readable, no infra for D0/D1
- **Follow-up:** Optional GitHub sync later (`devloop sync-gh`)

## ADR-0004 — MiniMax/Blackbox via AGENTS.md + skills

- **Date:** 2026-08-07
- **Decision:** Standard `AGENTS.md` + `.blackbox/skills` + portable `skills/`
- **Why:** Blackbox reads AGENTS.md/skills with minimal config; MiniMax can consume `devloop prompt`
- **Follow-up:** Keep prompts deterministic and issue-scoped

## ADR-0003 — Docs and devloop before product code

- **Date:** 2026-08-07
- **Decision:** Phases D0/D1 gate Phase 0+
- **Why:** Prevents aimless feature sprawl; enables AI-driven implementation
- **Follow-up:** Seed issues per phase on the board

## ADR-0002 — One central brain, many bodies

- **Date:** 2026-08-07
- **Decision:** Centralized sync server as source of truth; clients are presence/execution edges
- **Why:** “Everywhere + house + synced” without fragmented memories
- **Follow-up:** FastAPI brain on always-on home host

## ADR-0001 — Product is operator platform, not todo app

- **Date:** 2026-08-07
- **Decision:** Tasks/contacts/reminders are execution examples; architecture is Soul/Mind/Hands/Presence/House
- **Why:** User intent = Iron Man + Rick house AI, not Gemini with a checklist
- **Follow-up:** Life tools as plugins in Phase 3

## ADR-0011 — Pivot to TypeScript Web UI

- **Date:** 2026-08-09
- **Decision:** Use Vite + React + TypeScript + Vanilla CSS for the new web client.
- **Why:** The Flutter Windows desktop build was unreliable/hidden and lacked the granular CSS control needed for a rich glassmorphism UI. Web client gives maximum styling control.
- **Follow-up:** Replaces the Flutter UI as the primary modern interface.

## ADR-0012 � Physical CAD Generation via CadQuery

- **Date:** 2026-08-11
- **Decision:** Use Python-based cadquery library as the primary engine for LLM-driven hardware invention/CAD design.
- **Why:** CadQuery allows building parametric 3D models using a fluent Python API, which LLMs are very adept at writing. Unlike OpenSCAD which requires shelling out to a C++ binary and learning its DSL, CadQuery can directly export STLs in-process and integrates natively with Python ecosystem.
- **Follow-up:** Implemented prototype in scripts/research_cad.py.
