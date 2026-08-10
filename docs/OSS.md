# Open-source leverage

**Rule:** Prefer mature open-source building blocks over custom reinvention. Jarvis owns Soul/Mind/Hands *integration*, not commodity engines.

## Locked defaults (by area)

| Area | Phase | Choose | Avoid reinventing |
|------|-------|--------|-------------------|
| Brain API | 0+ | FastAPI + Uvicorn | Custom HTTP stack |
| Data | 0–2 | SQLite | Custom file DB |
| Semantic memory | 3+ | `sqlite-vec` first; ChromaDB if needed | Homegrown vector search |
| **Web presence (primary)** | 0+ | **Vite + React + TypeScript** — `clients/web/` | Treating Flutter as the default web UI |
| **Mobile/desktop presence (Field Body)** | 0+ | **Flutter + Dart** — `clients/flutter/` — bridge, client tools, confirmations; **not** chat UI | Duplicating `clients/web` chat in Flutter |
| **Windows legacy lane** | 0+ | **Flet + Python** — `clients/windows/` (tray, voice, bridge) | New Electron/Tauri without ADR |
| Android bridge stub | 0+ | Kotlin Compose stub in `clients/android/` | Full duplicate of Flutter + web |
| STT | 4 | **faster-whisper** (local); cloud optional | Cloud-only STT lock-in |
| TTS | 4 | **Piper** (primary); **Kokoro** optional via ADR | Paid TTS as default |
| House | 5 | **Home Assistant** as device fabric | Per-brand IoT drivers |
| Tool/runtime later | 6 | Python plugins + **optional** Lua/Go/R via [POLYGLOT_TOOLS.md](dev/POLYGLOT_TOOLS.md) | Monolithic new frameworks |

**Roles (human decision):** [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md).

## Principles

1. Brain stays the orchestration layer — OSS is *plugged in*, not forked randomly
2. Prefer **local/offline-capable** for voice and house control
3. One primary choice per concern; second option is fallback, not dual-support forever
4. Record swaps in [DECISIONS.md](DECISIONS.md)

## What Jarvis still owns

- Persona, memory policy, confirmations, sync identity
- Tool protocol and device bridges
- Multi-surface presence + house conversation continuity
- Devloop / agent-buildable process

## Dev tooling (integrate, don’t fork)

| Tool | Status |
|------|--------|
| Ruff, pre-commit, smoke_web | ✅ |
| pytest (deps), mypy, uv | pytest ✅ **119**; tests **115**; types **116** |

Install manifest (what to pip/npm when): [dev/STARK_OSS_INSTALL.md](dev/STARK_OSS_INSTALL.md).

Plan: [dev/OSS_DEV_PLAN.md](dev/OSS_DEV_PLAN.md) · [dev/OSS_ARSENAL.md](dev/OSS_ARSENAL.md) (17-tool map) · [dev/LAB_STACK.md](dev/LAB_STACK.md) · [dev/STARK_TIMELINE.md](dev/STARK_TIMELINE.md).
