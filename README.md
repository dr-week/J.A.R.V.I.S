# Jarvis

Jarvis is a personal AI that lives in your house, your pocket, and your browser.
One synced brain. Many bodies. It does not just answer questions; it executes
work, keeps continuity, and grows through real integrations.

Think:

- an operator-grade assistant with memory and tools
- a clean web chat as the primary interface
- phone, desktop, and home surfaces that extend the same mind

This repo is docs-first, agent-buildable, and board-driven. Code follows the
plan, not vibes.

## What Makes It Feel Modern

Jarvis is being built with current product patterns instead of a retro CLI-first
AI stack:

- server-owned keys and tool execution
- a primary web client with PWA-style daily use
- field/bridge clients for mobile, desktop, and house presence
- modular OSS integrations instead of custom reinvention
- docs, board, and implementation flow kept in sync so the product stays legible

The long-term goal is an assistant that feels ambient, fast, and trustworthy
without turning into a bloated app zoo.

## Demo in 5 minutes (presentation)

**Live pitch:** [docs/DEMO.md](docs/DEMO.md)

```powershell
# Windows — brain + web + browser
.\scripts\demo_up.ps1
```

```bash
# macOS / Linux
chmod +x scripts/demo_up.sh && ./scripts/demo_up.sh
```

Set `GEMINI_API_KEY` in `.env` (copy from `.env.example`) before you need real
chat. Architecture-only demos work with **LLM off** — the UI still pairs to the
brain and the product skeleton still shows up.

**Doc index (keep markdown aligned):** [docs/DOCS_MAP.md](docs/DOCS_MAP.md)

## Quick Start for Humans

1. Read [docs/VISION.md](docs/VISION.md), [docs/SCOPE.md](docs/SCOPE.md), [docs/STRATEGY.md](docs/STRATEGY.md), [docs/FUTURE.md](docs/FUTURE.md)
2. Check current work: [docs/board/NOW.md](docs/board/NOW.md)
3. Run the internal build loop (supports **2 parallel workers**):

```bash
python scripts/devloop.py status
python scripts/devloop.py next --owner cursor         # this IDE
python scripts/devloop.py prompt --owner antigravity  # other AI
# or: python scripts/devloop.py prompt --owner claude
python scripts/devloop.py loop                        # dual-AI feedback bus + LIVE_PLAN
python scripts/devloop.py sync --owner cursor         # refresh board + optional LIVE_BRIEF
python scripts/devloop.py brief --owner cursor        # dynamic instructions (not static)
```

Parallel rules: [docs/dev/PARALLEL.md](docs/dev/PARALLEL.md) · Onboard new AI: [docs/dev/AGENT_ONBOARDING.md](docs/dev/AGENT_ONBOARDING.md) · Feedback: [docs/dev/FEEDBACK_LOOP.md](docs/dev/FEEDBACK_LOOP.md)

## Quick Start for AI Agents

1. Read [AGENTS.md](AGENTS.md) — MiniMax also: [.blackbox/RULES.md](.blackbox/RULES.md) + [docs/dev/MINIMAX.md](docs/dev/MINIMAX.md)
2. Read [docs/board/NOW.md](docs/board/NOW.md) and [docs/SCOPE.md](docs/SCOPE.md)
3. Run `python scripts/devloop.py prompt` and execute that brief
4. When finished: `python scripts/devloop.py done ISSUE-XXX`

## Phase Map

| Phase | Name | Goal |
|-------|------|------|
| **D0** | Docs OS | Specs, board, agent contracts |
| **D1** | Devloop | Feedback-loop CLI for issues / next / done |
| **0** | Skeleton | Monorepo brain + Android + Web + Windows clients |
| **1** | Soul | Persona, memory, synced identity |
| **2** | Hands | Tool runtime, device bridges, audit |
| **3** | Life tools | First domain plugins (examples, not the ceiling) |
| **4** | Voice | STT/TTS, tray, wake word |
| **5** | House | Home hub, rooms, smart-home bridges |
| **6** | Expand | Tool SDK for endless integrations |

Full detail: [docs/ROADMAP.md](docs/ROADMAP.md) · Strategy: [docs/STRATEGY.md](docs/STRATEGY.md) · Future / levels: [docs/FUTURE.md](docs/FUTURE.md) · OSS: [docs/OSS.md](docs/OSS.md)

### Surface Roles

- **Daily Driver Chat**: the web client (`clients/web`) is the primary UI for
  chat and sessions. Install it as a PWA or desktop shortcut for a cleaner
  app-like feel.
- **Desktop Agent**: the Windows client (`clients/windows`) is not a second
  chat product. It is a tray agent for voice, device bridging, and background
  execution.
- **Field Body**: Flutter is the mobile/handheld control surface for bridge
  actions, confirmations, and lightweight presence.

## Plugins (Phase 3+)

### Velocity App Builder
To use the Velocity dev server through Jarvis, symlink your Velocity app directory via environment variable:
1. Set `JARVIS_VELOCITY_ROOT` (e.g. `JARVIS_VELOCITY_ROOT=e:\CODES\velocity`) in your OS environment or `.env`.
2. Run `.\scripts\boot_velocity.ps1` to link `plugins\velocity_builder`, install dependencies, and start the dev server.

## Layout

```
jarvis/
  AGENTS.md              # agent contract
  .blackbox/RULES.md     # Blackbox / MiniMax quick rules
  docs/                  # product + process truth
  docs/DOCS_MAP.md       # which docs mirror each other
  docs/board/            # living NOW / NEXT / DONE / issues
  skills/                # portable agent skills
  .blackbox/skills/      # Blackbox-native skills
  scripts/devloop.py     # internal AI app-dev feedback loop
  backend/               # (Phase 0+) central brain
  clients/               # (Phase 0+) android / windows / house
  tools/                 # (Phase 2+) tool plugins
```

## Status

D0/D1 done. Phase 0–1 largely shipped; **Phase 2 Hands** is in progress
(Windows bridge done, Android **033** next). Board: [docs/board/NOW.md](docs/board/NOW.md).
