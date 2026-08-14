# Jarvis design system

Canonical **visual and layout rules** for all Presence clients. **Stack roles** (what to build where): [dev/PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md) — **Vite web first**, Flutter experimental, Flet legacy Windows lane.

**Required reading before any UI issue:** [DESIGN.md](DESIGN.md) + [PRESENCE_STACKS.md](dev/PRESENCE_STACKS.md) + lane doc ([WEB_UI](dev/WEB_UI.md) · [FLUTTER_FIELD](dev/FLUTTER_FIELD.md) · [MINIMAX_UI](dev/MINIMAX_UI.md)).

---

## Principles

1. **One brain, many bodies** — chrome is familiar across surfaces; tokens and hierarchy stay aligned.
2. **Glass on motion** — panels use blur + subtle border on top of a **non-flat** background (gradient or mesh), never glass-on-pure-`#000` alone.
3. **Chat is the hero** — the message thread owns the main pane; navigation is secondary.
4. **Status is honest** — connection, LLM, and bridge state are visible once, in the designated status zone (see below).

---

## Anti-duplication (hard rule)

Do **not** ship duplicate chrome. Each concept appears **once** per screen.

| Concept | Where it lives | Do not also put it in… |
|---------|----------------|-------------------------|
| Product name (“Jarvis”) | **Brand zone** (sidebar header or compact top bar on phone) | Main chat header, page title, footer |
| Session / screen title | **Context line** (e.g. “Current session”) in nav or subtitle | Same text as product name |
| Connection + LLM status | **Status zone** (main header or footer — pick one per surface doc) | Sidebar and header |
| Bridge line | Same **status zone** as connection | Second footer line elsewhere |
| Primary send action | **One** composer button | Duplicate FAB or header send |
| Settings / New chat | **Nav rail or menu** — one control each | Two buttons for the same action |

Before merge: scan the tree for repeated labels, twin status dots, or two send buttons. Ensure that if a Sidebar is present, the main Chat Header does **not** repeat the "Jarvis" brand name.

---

## Design tokens (shared)

Use CSS variables (Web), `ThemeData` / constants (Flutter), or Flet theme keys (Windows) — **same names where possible**.

| Token | Role | Example (dark) |
|-------|------|----------------|
| `--bg-color` | Base canvas | `#0f0f13` |
| `--accent-color` | Primary actions, user bubbles | `#0a84ff` |
| `--text-main` / `--text-muted` | Body / secondary | `#f0f0f2` / `#8e8e93` |
| `--panel-bg` | Glass fill | `rgba(25,25,30,0.7)` |
| `--border-color` | Hairlines | `rgba(255,255,255,0.1)` |
| Glass blur | `backdrop-filter` | `24px` (Web); equivalent on other stacks |

### Motion & depth

To avoid flat UI, clients should implement:
- **Shadows**: Chat bubbles and floating panels should use a soft drop shadow (e.g., `0 4px 12px rgba(0, 0, 0, 0.15)`).
- **Backgrounds**: Do not use flat `#000` or `#111`. Use a slow, animated radial/mesh gradient to bring the glassmorphism to life.
- **Message Entry**: New chat bubbles must animate in (e.g., `slide-up` with a 0.3s duration).

Surface docs may add breakpoints and wireframes; **tokens and anti-duplication stay here**.

---

## Layout regions

Every client should map UI to these regions (names are logical, not file names):

```text
┌─────────────┬──────────────────────────────┐
│ BRAND       │ STATUS (dot + LLM + bridge)  │
│ NAV         ├──────────────────────────────┤
│             │ CHAT (scroll)                │
│             ├──────────────────────────────┤
│             │ COMPOSER (single send)       │
└─────────────┴──────────────────────────────┘
```

**Responsive Rule**: On **compact** widths (< 768px), the NAV must collapse into a mobile drawer (hamburger menu) or bottom bar. The main Chat Header takes over the BRAND zone on mobile, but never drop the status zone.

---

## Surface docs (required per lane)

| Client | Path | When to read |
|--------|------|----------------|
| Web (Vite/React) | [dev/WEB_UI.md](dev/WEB_UI.md) | `clients/web/**` |
| Flutter (Field Body) | [dev/FLUTTER_FIELD.md](dev/FLUTTER_FIELD.md) | `clients/flutter/**` — bridge, tools, confirm |
| Windows Flet | [dev/MINIMAX_UI.md](dev/MINIMAX_UI.md) | `clients/windows/ui_gui.py` |

---

## Acceptance hook

UI issues must cite the surface doc in **Lane** and verify:

- [ ] No duplicate brand, status, or primary actions (checklist above)
- [ ] Tokens match this doc or issue documents an intentional exception
- [ ] Motion & depth: mesh/gradient background, bubble shadows, message enter animation (see Motion & depth)

See [ACCEPTANCE.md](ACCEPTANCE.md) and [dev/DEFINITION_OF_DONE.md](dev/DEFINITION_OF_DONE.md).

**Open-source stack choices** (Flet, Flutter, Vite, etc.) live in [OSS.md](OSS.md). Update OSS only when you add or swap a **framework/library default**, not for every visual tweak.

---

## 🎨 Open-Source UI & Design Systems (Zero-Code Layouts)

Jarvis leverages top-tier open-source design components to eliminate custom CSS work:

1. **shadcn/ui Design System (121k⭐)**:
   - Token conventions, CSS variables (`--background`, `--card`, `--popover`, `--accent`).
   - Copy-paste accessible React components for dialogs, popovers, dropdowns, and buttons.
2. **Lucide Icons (15k⭐)**:
   - Unified icon language across Vite React web HUD and Flet desktop presence.
3. **Open-WebUI Layout Tokens (149k⭐)**:
   - Responsive multi-device chat layout, sidebar collapsing math, and dynamic mobile drawers (`100dvh`).

---

## Related

[DOCS_MAP.md](DOCS_MAP.md) · [PERSONA.md](PERSONA.md) · [REQUIREMENTS.md](REQUIREMENTS.md) (FR-P* presence) · [OSS.md](OSS.md)
