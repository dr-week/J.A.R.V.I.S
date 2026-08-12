# Roadmap — work divided by phases

Strategy: **docs and build OS first**, then Soul → Hands → Presence → House → Expand. Never skip the board.

**North star & levels:** [FUTURE.md](FUTURE.md) · **Doc sync:** [DOCS_MAP.md](DOCS_MAP.md) · **Strategy:** [STRATEGY.md](STRATEGY.md)

## Phase D0 — Docs OS (bootstrap — done)

**Goal:** Specs + agent contracts so Cursor / Antigravity / Claude can work cold.

- Product docs (vision, requirements, scope, architecture, persona, security…)
- Dev process docs
- Living board + issue files
- `AGENTS.md` + skills

**Exit:** All D0 issues done; agents can read `AGENTS.md` and pick `NOW`.

## Phase D1 — Devloop

**Goal:** Feedback-loop CLI automates issue lifecycle.

- `status`, `next`, `claim`, `issue`, `update`, `done`, `refresh`, `prompt`, `bootstrap`
- Board files stay source of truth
- **Epic: Tech Debt Decomposition (Pending):** Refactor the 40KB `devloop.py` monolith into a Typer-based modular architecture (`scripts/commands/` + `scripts/core/`) using Pydantic and Loguru.

**Exit:** Cold agent can run `devloop prompt` and receive a complete work package.

## Phase 0 — Skeleton

**Goal:** Monorepo boots; clients talk to brain.

- `backend/` FastAPI health + auth pairing stub
- `clients/android` + `clients/windows` minimal chat against brain
- Shared OpenAPI / schemas stub

**Exit:** Send a message from phone or PC and get a streamed reply from the brain (no tools yet).

**Presence note (2026-08):** Canonical **chat** UI is `clients/web/`. Kotlin Android (`clients/android`) and Flutter Field prove **pair + bridge + confirm**; Windows Flet is tray/voice. Do not add parallel chat products. See [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md) · [dev/MAJOR_WORK_PLAN.md](dev/MAJOR_WORK_PLAN.md) **M-Android**.

## Phase 1 — Soul (done)

**Goal:** Feels like *your* assistant.

- Persona config
- Memory CRUD + injection
- Synced profile across devices
- Proactive habits surfaced

**Exit:** Fact stored on one device recalled on another, and habits proactively surface in the prompt. (Done)

## Phase 2 — Hands

**Goal:** Execution runtime exists.

- Tool protocol + registry ✅ (030)
- Confirmations + action audit ✅ (031)
- Windows device bridge ✅ (032 — MiniMax: WS `tool_execute` / `tool_result`, see [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md))
- Android device bridge ✅ (033)

**Exit:** Agent completes a multi-step device action with an audit entry.  
**Proof (Windows):** `python scripts/proof_phase2_windows.py` — two `windows_open` steps + `action_log` (ISSUE-147).  
**Android:** bridge/Presence UI (033/150); multi-step live-device demo is follow-up, not blocking this exit.

## Phase 3 — Life tools

**Goal:** First useful domains as plugins (examples, not ceiling).

- Starter plugins: admin samples (tasks/reminders/plan), calendar/files/web as chosen
- Non-Google connector slot #1

**Exit:** At least 3 domain tools pass acceptance samples from REQUIREMENTS examples. *(Done — HA, Reminders, and Tasks plugins tested and proven)*  
**Proof:** `pytest backend/tests/test_phase3_life_tools.py` — `reminder_set`/`reminder_list`, `weather_current`, `home_scene` (ISSUE-149).

## Phase 4 — Voice + presence

**Goal:** Always-there feel on phone/PC.

- STT/TTS
- Tray / quick tile
- Optional wake word
- Push sync polish

**Exit:** Hands-free turn on one client; state mirrors elsewhere. *(Done — Windows Flet UI supports `wake_word` and TTS hands-free loops while running in tray)*

## Phase 5 — House body

**Goal:** Rick-layer — AI in the house.

- Home hub hardening ✅ (060) — always-on run mode in [HOME_HUB.md](HOME_HUB.md)
- Home Assistant bridge ✅ (061) — plugin under `backend/plugins/homeassistant/`
- Room presence / continue conversation across rooms
- Basic scenes by voice

**Exit:** Start request in a room; continue on phone; run a home scene.

## Phase 6 — Expand forever

**Goal:** Tool SDK; endless integrations without redesigning the brain.

- Documented plugin template
- Versioned tool schema
- Example third-party connectors

**Exit:** New tool added via plugin docs alone (no core rewrite).

## Phase 7 — The Stark Endgame

**Goal:** An omnipresent, predictive entity with physical agency.

- Predictive Analytics Engine (Proactive actions)
- Spatial AR Computing Interface
- Continuous Local LLM Fine-Tuning (Synapse Protocol)
- Physical Actuation via ROS2

**Exit:** Jarvis predicts a need, alerts you in AR, and physically acts on the world without a manual trigger.

## Phase 8 — The Enterprise Protocol

**Goal:** An Autonomous Business Operating System.

- AI Corporate Hierarchy (AI CEO, Scout, Builder, Analytics)
- Continuous Market Hunting (Reddit, App Store, SaaS directories)
- Autonomous Micro-Experimentation (Landing pages, Waitlists)
- Revenue as the primary fitness feedback loop (Stripe integration)

**Exit:** Jarvis autonomously finds a gap, builds a product via Velocity, drives traffic, and achieves a >1% conversion rate to generate its first automated dollar, while you act as the Chairman.

## Phase 9 — The Forge Protocol

**Goal:** Physical Manufacturing Integration.

- Parametric CAD generation (OpenSCAD/Python)
- Physics Simulation validation
- Direct G-Code streaming to 3D printers and CNCs

**Exit:** Jarvis autonomously designs a physical object in 3D and manufactures it on a local 3D printer without manual slicing.

## Phase 10 — The EDITH Protocol

**Goal:** Global Telemetry & Swarm Robotics.

- Integration with Global APIs (Weather, Supply Chain, OSINT)
- Mesh Network Deployment (Iron Legion nodes on edge devices)
- Swarm coordination algorithms

**Exit:** Jarvis coordinates a task across multiple physical edge devices located in different geographic areas.

## Phase 11 — The Neural Link

**Goal:** Zero-Latency Brain-Computer Interface.

- BCI hardware integration (e.g., OpenBCI)
- EEG signal to intent translation
- UI/UX bypass

**Exit:** A user intent is read from a BCI headset and executed by Jarvis without any spoken or typed command.

---

## Priority rules

1. Finish D0 → D1 before Phase 0 code sprawl
2. Within a phase, P0 issues before P1/P2
3. One NOW focus (max 3) — see board
4. Cross-phase work only via explicit issue

## Dependency graph

```text
D0 → D1 → 0 → 1 → 2 → 3
                 ↘ 4
            2/3/4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
```
