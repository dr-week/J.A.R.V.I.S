---
name: jarvis-product
description: Product constraints for Jarvis — intimate executable personal AI in-house and everywhere. Use when implementing assistant behavior, tools, persona, sync, or house features.
---

# Jarvis product skill

## North star

Close personal operator (Jarvis/Friday) + ambient house AI (Rick vibe). Executes via tools. One synced brain. Many bodies.

**Vision arc:** [docs/FUTURE.md](../docs/FUTURE.md) · [docs/PARTNERSHIP.md](../docs/PARTNERSHIP.md) · [docs/VISION.md](../docs/VISION.md) · Doc index: [docs/DOCS_MAP.md](../docs/DOCS_MAP.md)

**Blackbox mirror:** [.blackbox/skills/jarvis-product/SKILL.md](../.blackbox/skills/jarvis-product/SKILL.md) — keep Do/Don't in sync.

## Do

- Prefer tools over instructions
- Keep persona per `docs/PERSONA.md`
- Confirm high-risk actions
- Implement life domains as plugins
- Treat tasks/contacts/reminders as **examples**, not the whole product

## Don't

- Build a Google-only assistant
- Trap memory in one device
- Ship API keys in clients
- Expand SCOPE silently
- Pretend a tool succeeded when it failed
- **Rebuild the same chat UI in another client** (Flutter/Flet) when `clients/web` should own it — see [docs/dev/PRESENCE_STACKS.md](../docs/dev/PRESENCE_STACKS.md)

## Architecture anchors

Soul / Mind / Hands / Presence / House body — see `docs/ARCHITECTURE.md`, `docs/GLOSSARY.md`, `docs/SYNC_PROTOCOL.md`.

**Presence UI:** [docs/DESIGN.md](../docs/DESIGN.md) — required for any client chrome or layout change.
