# Jarvis UI Design System & Component Token Specs

> **Canonical Reference:** Complete tokens, color scales, glassmorphism math, layout primitives, and component hierarchy for all Jarvis Presence interfaces (Vite Web, Flutter Mobile, Desktop).

---

## 1. Unified Token Matrix

```css
:root {
  /* Surface Canvas */
  --bg-canvas: #070709;
  --bg-subtle: #0f0f14;
  --bg-glass-panel: rgba(18, 18, 24, 0.72);
  --bg-glass-card: rgba(26, 26, 36, 0.65);
  
  /* Borders & Hairlines */
  --border-glass: rgba(255, 255, 255, 0.08);
  --border-focus: rgba(10, 132, 255, 0.55);
  --border-success: rgba(48, 209, 88, 0.35);
  
  /* Typography Colors */
  --text-primary: #f5f5f7;
  --text-secondary: #9898a0;
  --text-tertiary: #636366;
  --text-accent: #0a84ff;
  
  /* Semantic Action Tokens */
  --color-brand: #0a84ff;         /* Jarvis Neon Blue */
  --color-success: #30d158;       /* Trade Profit / Online */
  --color-warning: #ffd60a;       /* Risk Alert / Approaching Cap */
  --color-danger: #ff453a;        /* Blocked Execution / Loss */
  --color-purple: #bf5af2;        /* AI Reasoning / Strategy */
  
  /* Elevation & Motion */
  --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  --shadow-glow-cyan: 0 0 24px rgba(10, 132, 255, 0.25);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;
  --transition-fast: 150ms cubic-bezier(0.16, 1, 0.3, 1);
  --transition-smooth: 250ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 2. Component Primitives

### 2.1 The Glass Card (`<GlassCard />`)
```tsx
// Standardized Glass Card wrapper for Widgets and Radar Feeds
<div className="backdrop-blur-xl bg-card/65 border border-white/10 rounded-2xl p-4 shadow-glass transition-all hover:border-white/20 hover:shadow-glow-cyan">
  {children}
</div>
```

### 2.2 The Confirmation Gate Sheet (`<RiskGateModal />`)
When any dangerous tool (`confirm_always`) triggers:
- **Backdrop:** `backdrop-blur-md bg-black/60`
- **Card:** Red/Orange rim glow (`border-amber-500/40`)
- **Primary CTA:** Double-state Confirm Button (`"Execute Trade: AAPL $500"`)
- **Secondary CTA:** Ghost Dismiss Button (`"Cancel Action"`)

### 2.3 Financial KPI Metric Capsule (`<MetricCapsule />`)
- Compact horizontal layout with label, live value in INR/USD (`₹4,850.00` / `$120.50`), and trend delta chip (`+12.4%`).
