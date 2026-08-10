# Web UI — Vite + React (`clients/web/`)

**Role:** **Primary** presence client (TypeScript). Parent: [DESIGN.md](../DESIGN.md). Stacks: [PRESENCE_STACKS.md](PRESENCE_STACKS.md).

---

## Regions (this surface)

| Region | Element | Notes |
|--------|---------|--------|
| Brand | `.sidebar-header` | **Only** place for the word “Jarvis” + logo icon |
| Nav | `.sidebar-item` + `.session-list` | Chat/settings tabs; **recent sessions** (FR-P3, ISSUE-102) |
| Status | `.header` (main column) | Status dot + `statusLine` + `bridgeStatus` — **no** second product title |
| Chat | `.chat-container` | Scrollable thread |
| Composer | `.composer-container` | Single text field + **one** send button |

Do **not** add “Jarvis Web”, duplicate bot icons, or a second status dot in the main header.

---

## Visual

- Background: animated mesh in `index.css` (`body::before`) — see DESIGN.md glass-on-motion rule.
- Panels: `.glass-panel` — blur `24px`, inset highlight, soft shadow.
- Bubbles: user / assistant / system styles in `App.css`; one shadow tier per role.

---

## Breakpoints

Align with [DESIGN.md](../DESIGN.md) **Responsive rule** (`< 768px` compact).

| Width | Layout |
|-------|--------|
| `< 768px` | NAV collapses to drawer or bottom bar; **brand** in mobile top bar if no sidebar; status zone preserved |
| `≥ 768px` | Two-column: sidebar (brand + nav) + main; main header = **status only** (no duplicate “Jarvis”) |

Until a hamburger ships, use the mobile menu control in `App.tsx` (ISSUE-098/105).

---

## Sessions (FR-P3)

- On connect: `brainApi.listSessions()` → `GET /sessions`
- Sidebar list; click → `getSession(id)` → `GET /sessions/{id}`; set `sessionId` and hydrate messages
- **New chat** generates a fresh `sessionId` (brain creates thread on next `/chat`)
- Session UI is **web-only** — Flutter Field does not list sessions ([FLUTTER_FIELD.md](FLUTTER_FIELD.md))

---

## Brain connection

- API base: `http://localhost:8787` (dev); see `clients/web/README.md`.
- Start brain from **repo root**: `python -m uvicorn backend.app.main:app --port 8787`.
- Pairing secret must match repo `.env` (`JARVIS_PAIRING_SECRET`).

---

## Verify

```bash
cd clients/web
npm run dev
```

- Header shows status only (no duplicate brand).
- One send button; sidebar shows brand once.
- `npm run build` succeeds.

---

## Related

[DESIGN.md](../DESIGN.md) · [FLUTTER_UI.md](FLUTTER_UI.md) · [MINIMAX_UI.md](MINIMAX_UI.md) · Stack defaults: [OSS.md](../OSS.md) (Vite/React row)
