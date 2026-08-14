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

## 🎨 Canonical Zero-Code UI Design System Stack (`clients/web`)

Jarvis standardizes on **Tailwind CSS + shadcn/ui + Lucide React** as the canonical zero-code UI design system stack for the web presence (`clients/web`):

1. **Tailwind CSS (Utility-First Design Engine)**:
   - Atomic utility styling wired to unified design tokens via CSS variables (`--background`, `--card`, `--primary`, `--accent`, `--border`, `--ring`).
   - Dynamic responsiveness and glassmorphism styling (`backdrop-blur-xl`, `bg-card/70`, `border-border/40`) without hand-written media queries or custom CSS classes.
2. **shadcn/ui Design System (121k⭐ Primitives)**:
   - Copy-paste accessible components built on headless Radix UI primitives.
   - Built-in accessible dialogs, popovers, dropdown menus, tabs, tooltips, and buttons that automatically adhere to theme tokens.
3. **Lucide Icons (15k⭐ / `lucide-react`)**:
   - Canonical icon language across Vite React web HUD and desktop presence, providing consistent visual symbols for actions, status indicators, and tools.
4. **Open-WebUI Layout Tokens (149k⭐ Inspiration)**:
   - Responsive multi-device chat layout, sidebar collapsing math, and dynamic mobile drawers (`100dvh`).

---

## ⚡ How Zero-Code CSS Tokens Save 90% of Custom UI Styling Work

Adopting tokenized Tailwind CSS and shadcn/ui components eliminates roughly **90% of bespoke UI styling and CSS maintenance overhead**:

1. **Elimination of Bespoke CSS Boilerplate**:
   - Instead of writing and maintaining hundreds of lines of fragile CSS classes (`.chat-bubble-user`, `.modal-overlay`, `.dropdown-item`), developers style interfaces inline with standardized semantic utility classes (`bg-primary text-primary-foreground rounded-2xl shadow-sm`).
2. **Unified Semantic Token System**:
   - Color palettes, spacing scales, border radiuses, and glass blur factors are defined **once** in CSS variables (e.g., `--background`, `--accent`, `--panel-bg`). All components automatically inherit theme modes (dark/light) and visual depth without manual override rules.
3. **Out-of-the-Box Glassmorphism & Depth**:
   - Modern HUD aesthetics (frosted glass panels, subtle border highlights, drop shadows, and radial glow effects) are composed with modular Tailwind utilities (`backdrop-blur-md bg-card/60 border border-white/10 shadow-lg`) rather than bespoke cross-browser CSS hacks.
4. **Zero Layout & Accessibility Thrash**:
   - Components from shadcn/ui include full WAI-ARIA compliance, focus trapping, keyboard navigation, and responsive collapse logic out of the box, saving days of writing accessible boilerplate.
5. **AI-Friendly & Maintainable**:
   - LLM coding agents can reliably generate, refactor, and review tokenized utility class combinations without risking CSS specificity conflicts or cascading regression bugs across the application.

---

## Related

[DOCS_MAP.md](DOCS_MAP.md) · [PERSONA.md](PERSONA.md) · [REQUIREMENTS.md](REQUIREMENTS.md) (FR-P* presence) · [OSS.md](OSS.md) · [dev/WEB_UI.md](dev/WEB_UI.md)
