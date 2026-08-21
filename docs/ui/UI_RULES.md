# Jarvis UI Rules & Simplification Architecture

> **Primary Objective:** Build an ultra-fast, clean, and distraction-free user interface across Web, Mobile (Flutter/Android), and Desktop (Windows) with **zero visual bloat**.

---

## 1. Core Simplification Principles

### Rule 1: The "One Screen, One Truth" Rule
- **Chat is the Hero:** The conversation timeline and active tools own the viewport. Navigation, settings, and drawer panels stay unobtrusive and collapse automatically.
- **Single Status Indicator:** Connection status (Online/Offline), LLM engine, and Bridge health are displayed in **exactly one status pill** in the top bar. No duplicate badges across sidebar and headers.
- **No Duplicate Actions:** A single floating or bottom-docked composer for input. Never render duplicate send buttons or duplicate floating action buttons (FAB).

### Rule 2: 3-Second Cognitive Load
- A user must understand the state of their system within 3 seconds of glancing at the screen.
- Key financial numbers (Active Alerts, Arbitrage Gaps, Freebies Count, Portfolio Health) must use high-contrast primary tokens with semantic colors:
  - 🟢 **Green (`#30d158` / `--color-success`):** Profitable signal, active connection, positive cash flow.
  - 🟡 **Yellow (`#ffd60a` / `--color-warning`):** Pending confirmation, high volatility, approaching budget limit.
  - 🔴 **Red (`#ff453a` / `--color-danger`):** Gate block, rejected risk check, connection lost.

### Rule 3: Anti-Lag & Flat Hierarchy
- **Zero Heavy Render Trees:** No nested cards deeper than 2 layers.
- **Micro-Animations with Fixed Bounds:** Transitions must be under `200ms` (`ease-out`). Avoid long bouncing physics that slow down execution.
- **Virtual Scrolling:** All message feeds and scraped opportunity lists must use virtualized lists (`react-window` or Flutter `ListView.builder`) to handle 10,000+ items at 60 FPS without memory bloat.

---

## 2. Interaction & Confirmation Gate Rules

### Dangerous Tool Execution (Financial Actions / Outreach)
1. **Interactive Modal / Sheet:** When a tool with `risk_level: "confirm_always"` triggers (e.g. sending a lead email or executing an order), the UI immediately displays a translucent confirmation sheet.
2. **Clear Parameter Diff:** Displays the exact payload in clean, human-readable format:
   - Target recipient / Asset ticker
   - Action summary & cost
   - "Confirm Execution" (Primary Accent) vs "Cancel" (Subtle Ghost Button)
3. **No Accidental Taps:** Destructive actions require either a double-tap confirmation or a swipe-to-execute gesture on mobile.

---

## 3. Visual Tokens & Typography Standards

| Token | CSS Variable | Flutter Theme | Value (Dark Theme) |
|---|---|---|---|
| Canvas Background | `--bg-base` | `theme.scaffoldBackgroundColor` | `#0a0a0c` |
| Glass Surface | `--surface-glass` | `Colors.white.withOpacity(0.06)` | `rgba(22, 22, 28, 0.75)` |
| Primary Accent | `--accent-primary` | `Color(0xFF0A84FF)` | `#0a84ff` (Neon Cyan/Blue) |
| Success Accent | `--accent-success` | `Color(0xFF30D158)` | `#30d158` |
| Text Primary | `--text-primary` | `Color(0xFFF5F5F7)` | `#f5f5f7` |
| Text Muted | `--text-muted` | `Color(0xFF86868B)` | `#86868b` |
| Border Hairline | `--border-subtle` | `Color(0x1FFFFFFF)` | `rgba(255, 255, 255, 0.08)` |

---

## 4. UI Checklist for Pull Requests / Merges

- [ ] Does every action complete in ≤ 2 clicks/taps?
- [ ] Is the interface readable on low-brightness mobile screens?
- [ ] Are all financial tickers and live deals displaying real timestamps?
- [ ] Does the UI handle zero-network / backend-reconnecting gracefully without blank screen crashes?
- [ ] Are all fonts system-native (`Inter`, `-apple-system`, `Roboto`, `Segoe UI`) to eliminate font download delays?
