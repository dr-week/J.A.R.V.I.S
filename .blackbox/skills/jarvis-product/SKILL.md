---
name: jarvis-product
description: Jarvis product constraints — personal executable AI, house + everywhere, synced brain.
---

# Jarvis product (Blackbox)

**Portable skill (keep in sync):** [skills/jarvis-product/SKILL.md](../../skills/jarvis-product/SKILL.md)  
**Doc map:** [docs/DOCS_MAP.md](../../docs/DOCS_MAP.md)

## North star

Close personal operator (Jarvis/Friday) + ambient house AI (Rick vibe). Executes via tools. One synced brain. Many bodies.

Long arc: [docs/FUTURE.md](../../docs/FUTURE.md) · Co-build: [docs/PARTNERSHIP.md](../../docs/PARTNERSHIP.md) · [docs/VISION.md](../../docs/VISION.md)

## Do

- Prefer tools over instructions
- Keep persona per `docs/PERSONA.md`
- Confirm high-risk actions
- Implement life domains as plugins
- Use **shadcn/ui + Tailwind CSS + Lucide React** design tokens for zero-code UI components (see `docs/DESIGN.md`)
- Treat tasks/contacts/reminders as **examples**, not the whole product

## Don't

- Build a Google-only assistant
- Trap memory in one device
- Ship API keys in clients
- Expand SCOPE silently
- Pretend a tool succeeded when it failed
- **Rebuild the same chat UI in another client** when web owns it — [PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md)

## Architecture anchors

Soul / Mind / Hands / Presence / House body — `docs/ARCHITECTURE.md`, `docs/GLOSSARY.md`, `docs/SYNC_PROTOCOL.md` (device bodies).

**Presence UI:** [docs/DESIGN.md](../../docs/DESIGN.md) — required for client chrome/layout.
