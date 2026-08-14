# Web UI — Vite + React (`clients/web/`)

**Role:** **Primary** presence client (TypeScript).  
**Canonical UI Stack:** **Tailwind CSS + shadcn/ui + Lucide React** (Zero-Code Design System).  
Parent: [DESIGN.md](../DESIGN.md). Stacks: [PRESENCE_STACKS.md](PRESENCE_STACKS.md).

---

## Canonical Zero-Code UI Stack

Jarvis Web (`clients/web`) uses **Tailwind CSS + shadcn/ui + Lucide React** as the canonical design system to build an ultra-responsive, accessible HUD interface without writing custom ad-hoc CSS:

- **Tailwind CSS**: Utility-first CSS engine mapped to design tokens via standard CSS variables (`--background`, `--card`, `--primary`, `--accent`, `--border`, `--ring`).
- **shadcn/ui**: High-quality, accessible Radix UI component primitives (Dialog, DropdownMenu, Tooltip, ScrollArea, Popover, Button).
- **Lucide React (`lucide-react`)**: Clean, consistent icon set matching desktop and field clients.

---

## ⚡ How Zero-Code CSS Tokens Save 90% of Custom UI Styling Work

Using standardized design tokens with Tailwind CSS and shadcn/ui slashes custom UI styling and CSS maintenance by **90%**:

1. **No Bespoke CSS Selectors**:
   - Eliminates bloated CSS stylesheets and manual class naming conventions (e.g. `.custom-chat-bubble-v2`). Everything is styled inline with standardized tokens (`bg-card/70 backdrop-blur-xl border border-white/10 text-foreground`).
2. **Instant Theming & Glassmorphism**:
   - Design tokens defined once in root CSS variables (`--bg-color`, `--accent-color`, `--panel-bg`) drive both light/dark modes and frosted glass styling across every component automatically without duplicate CSS rules.
3. **Turnkey Accessibility & State Handling**:
   - shadcn/ui primitives handle keyboard focus, ARIA attributes, modals, and dropdown transitions out of the box, saving hundreds of hours of custom interaction code.
4. **Responsive Layouts without Media Query Hacks**:
   - Tailwind breakpoint modifiers (`md:`, `lg:`) and dynamic viewport units (`100dvh`) handle desktop-to-mobile drawer collapsing cleanly without brittle custom `@media` blocks.
5. **Conflict-Free Agent Development**:
   - Coding agents (Cursor, Antigravity, MiniMax) can compose and refactor UI components rapidly using atomic utility classes without inducing CSS specificity conflicts or cross-file stylesheet regressions.

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
- Panels: `.glass-panel` or Tailwind `backdrop-blur-xl bg-card/70 border border-white/10 shadow-lg`.
- Bubbles: user / assistant / system styles; one shadow tier per role.

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

[DESIGN.md](../DESIGN.md) · [FLUTTER_UI.md](FLUTTER_UI.md) · [MINIMAX_UI.md](MINIMAX_UI.md) · Stack defaults: [OSS.md](../OSS.md) (Vite/React row) · [STARK_OSS_INSTALL.md](STARK_OSS_INSTALL.md)

