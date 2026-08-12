---
inclusion: fileMatch
fileMatchPattern: ['clients/web/**', 'clients/flutter/**', 'clients/windows/ui_gui.py', 'clients/windows/client.py']
---

# Jarvis UI design rules

Before editing UI code:

1. Read [docs/dev/PRESENCE_STACKS.md](docs/dev/PRESENCE_STACKS.md) — **Vite web first**; Flutter experimental; Flet legacy.
2. Read [docs/DESIGN.md](docs/DESIGN.md).
2. Read the surface doc for your lane:
   - Web (chat product) → [docs/dev/WEB_UI.md](docs/dev/WEB_UI.md)
   - Flutter (Field Body) → [docs/dev/FLUTTER_FIELD.md](docs/dev/FLUTTER_FIELD.md)
   - Flet Windows → [docs/dev/MINIMAX_UI.md](docs/dev/MINIMAX_UI.md)

## Hard constraints

- **One** product name / brand zone per screen.
- **One** status zone (connection, LLM, bridge) — not repeated in sidebar and header.
- **One** primary send/submit control in the composer.
- No placeholder nav buttons that duplicate an existing control; disable or hide until wired.
- Use shared tokens from DESIGN.md; do not invent one-off colors without an issue note.

## Done check

Scan the diff for duplicate labels (“Jarvis”, “Web”, “Settings”), twin status indicators, or two send buttons.
