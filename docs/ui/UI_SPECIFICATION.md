# Jarvis UI Specification & HUD Layout Design

> **Layout Architecture:** A modular, adaptive HUD system providing real-time intelligence feeds, assistant conversation, and rapid execution widgets.

---

## 1. Multi-Surface Responsive Layout

```text
================================================================================
| DESKTOP / TABLET LANDSCAPE (>= 1024px)                                       |
================================================================================
|  NAV RAIL   |            MAIN CHAT & EXECUTION HERO           |  OPPORTUNITY |
| (Collapsible|                                                 |   RADAR      |
|  64px/220px)|  [Top Bar: Status • Model • Risk Gate Indicator]|  (Deals,     |
|             |-------------------------------------------------|   Loot &     |
| • Chats     |                                                 |   Signals)   |
| • Money     |  [Conversation Timeline / Active Tool Output]   |              |
|   Maker     |                                                 | • Live ₹/$   |
| • Automate  |                                                 | • Arbitrage  |
| • Settings  |-------------------------------------------------| • Freebies   |
|             |  [Composer: Prompt Input + Mic + Send Action]   |              |
================================================================================

================================================================================
| MOBILE PORTRAIT (< 768px)                                                    |
================================================================================
| [Top Bar: Hamburger Nav | Brand | Brain Status Pill | Radar Tab]             |
|------------------------------------------------------------------------------|
|                                                                              |
| [Chat Timeline / Dynamic Tool Visualizer Cards]                              |
|                                                                              |
|------------------------------------------------------------------------------|
| [Floating Bottom Bar: Quick Pill Prompts ("Scan Deals", "Market Check")]     |
| [Docked Composer + Voice STT Button]                                         |
================================================================================
```

---

## 2. Component Specifications

### 2.1 The Top Status Bar
- **Position:** Fixed top header (`56px` height), sticky backdrop blur (`20px`).
- **Elements:**
  1. **Brain Connection Pill:** Green pulse dot + `"Brain Online"` (WebSocket active).
  2. **Active Engine Tag:** `"Gemini 2.0 Flash"` / `"LangGraph Router"`.
  3. **Risk Shield:** Icon indicator showing current safety level (`Strict Gate` / `Autonomous`).

### 2.2 The Money Maker "Opportunity Radar" Widget
- **Purpose:** Displays high-priority live updates from the intelligence & financial scanners without interrupting the chat flow.
- **Card Hierarchy:**
  - **Header:** Tag name (e.g. `India Loot`, `Tech Grant`, `Arbitrage Signal`).
  - **Headline:** Bold 1-line summary (e.g. `Free ₹1000 Cloud Credit - AWS Activate`).
  - **Action Button:** Quick 1-tap link out (`"View Offer"`) or 1-tap assistant trigger (`"Analyze with Jarvis"`).

### 2.3 Interactive Tool Result Cards (In-Chat)
When tools execute (`mm_scan_market`, `mm_scan_freebies_and_deals`), they output rich, tokenized JSON cards rather than raw terminal text:
```text
┌─────────────────────────────────────────────────────────────┐
│ ⚡ Tool Execution: mm_scan_market                            │
├─────────────────────────────────────────────────────────────┤
│ • AAPL: $224.50  | SMA-50: $218.30  | Trend: 🟢 Bullish     │
│ • BTC : $64,200  | SMA-50: $61,100  | Trend: 🟢 Momentum    │
│ • TSLA: $212.10  | SMA-50: $220.40  | Trend: 🔴 Bearish     │
├─────────────────────────────────────────────────────────────┤
│ Actions: [ Deep Technical Analysis ]   [ Generate Forecast ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Screen States & Fallbacks

1. **Disconnected State:** Amber banner appears above composer (`"Reconnecting to local brain (ws://localhost:8787)..."`) with cached historical data accessible.
2. **Confirmation Required State:** Screen dims to 60% opacity with a frosted card focusing attention on the action being reviewed.
3. **Empty State:** Clean 4-card launcher with quick prompts:
   - 💰 *"Scan today's Indian deals & cashback"*
   - 📈 *"Check tech stock moving averages"*
   - 💡 *"Generate 3 business ideas from AI news"*
   - ✉️ *"Draft freelance outreach for scraping gig"*
