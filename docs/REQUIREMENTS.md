# Requirements

## Problem

Consumer assistants (e.g. Gemini on Android) often **chat well but execute poorly**: cannot reliably edit prior work, manage subtasks, set reminders, edit a specific contact, plan a day, drive non-Google apps, or operate a house. Users want a **close personal operator** — Jarvis/Friday energy, ambient like Rick’s house AI — that lives everywhere and **does things**.

## Goals

1. **Intimate** — long-term memory of prefs, people, routines, projects
2. **Agentic** — multi-step goals completed via tools, not instructions-only replies
3. **Everywhere** — same mind on phone, PC, and **web**; continuous thread (chat UI: `clients/web/`)
4. **In-house** — ambient presence at home; control home systems
5. **Synced** — one centralized brain; clients are bodies
6. **Expandable** — new powers = plugins, not a new product
7. **Agent-buildable** — this repo itself is driven by docs + `devloop` so Cursor / Antigravity / Claude can implement safely

## Functional requirements

### Soul

- FR-S1: Persistent user profile and memories
- FR-S2: Configurable persona (name, tone) per [PERSONA.md](PERSONA.md)
- FR-S3: Preference learning and retrieval into each turn
- FR-S4: Synced identity across all paired devices/house nodes
- FR-S5: Passive observation — log interaction timestamps, topics, context with no user effort
- FR-S6: Habit detection — autonomously identify recurring behavioural patterns (daily/weekly cycles) from logged interactions
- FR-S7: Behavioural fingerprinting — learn writing style, response length preference, workflow rhythms
- FR-S8: Proactive trigger engine — surface learned-habit suggestions at the right moment without user prompting

### Mind

- FR-M1: Conversational interface (text; voice in Phase 4+)
- FR-M2: Tool-calling agent loop (plan → act → verify → report)
- FR-M3: Confirmation policy for destructive/sensitive actions
- FR-M4: Action audit log

### Hands (execution)

- FR-H1: Device bridges (Android intents/deep links; Windows open app/file/URL)
- FR-H2: Pluggable life-domain tools (calendar, comms, files, web, admin examples…)
- FR-H3: Third-party / non-Google integrations via tool registry
- FR-H4: Home device control via house hub bridge (Phase 5)

### Presence

- FR-P1: Android client presence — **device bridge** (`clients/android/`); chat via **web**, not a second full chat app
- FR-P2: Windows client presence — **tray/voice/bridge** (`clients/windows/`); chat via **web** where possible
- FR-P3: Continuous session sync across surfaces — brain `/sessions`; **canonical UI** lists/resumes in `clients/web/` ([PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md))
- FR-P4: Voice I/O + optional wake word (Phase 4) — Windows lane
- FR-P5: House room presence (Phase 5)
- **FR-P-web:** Primary conversational UI — **Vite + TypeScript** (`clients/web/`)

### Build OS (meta)

- FR-B1: Spec pack in `docs/`
- FR-B2: Living board (`NOW` / `NEXT` / `DONE` / issues)
- FR-B3: `scripts/devloop.py` feedback loop
- FR-B4: `AGENTS.md` + skills for Cursor, Antigravity, Claude (and optional other agents)

## Non-functional requirements

- NFR-1: Secrets never shipped in client binaries
- NFR-2: Local-first control plane (brain on home hub / user machine); cloud LLM optional
- NFR-3: Last-write-wins sync in v1; conflict strategy documented
- NFR-4: Opt-in always-on mics per room
- NFR-5: Issues sized for a single agent session when possible
- NFR-6: Docs and board stay git-friendly (markdown)

## Out of scope for requirements detail

See [SCOPE.md](SCOPE.md). Movie-level omnipotence is a **direction**, delivered phase by phase.
