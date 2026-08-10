# Flutter client — Field Body (not the chat app)

**Web owns:** chat, threads, sessions, settings, visual design → `clients/web/` (Vite + TypeScript).

**Flutter owns:** the **phone pocket body** — stay registered with the brain, run **client-executor** tools, and handle **confirmations** when you are away from the desk. No duplicate chat product.

Canonical stack roles: [PRESENCE_STACKS.md](PRESENCE_STACKS.md).

---

## Product name (working)

**Jarvis Field** — the device that *does things* and *approves things*, not the place you read long conversations.

---

## User jobs (Flutter only)

| Job | Why not web |
|-----|-------------|
| **Stay bridged** | Background-friendly WS `register` + reconnect; brain routes `tool_execute` to this `device_id` ([SYNC_PROTOCOL.md](../SYNC_PROTOCOL.md)). |
| **Execute client tools** | Desktop/window tools routed to Flutter **only where it is the registered bridge** — **not** `android_open` (Kotlin owns Android per ISSUE-033) |
| **Approve / deny** | After ISSUE-104: WS `confirm_request`; until then web chat text confirm ([hands/gate.py](../../backend/app/hands/gate.py)) |
| **Glance status** | “Brain online · 2 pending · last action …” — not a message thread. |
| **Open full chat** | Deep link / browser custom tab to **web** URL — one tap, no second composer. |

---

## Screens (target layout)

```text
┌─────────────────────────┐
│ Field · ● Online        │
├─────────────────────────┤
│ Pending confirmations   │
│  [ Approve ] [ Deny ]   │
│                         │
│ Recent device actions   │
│  android_open …         │
├─────────────────────────┤
│ [ Open full assistant ] │  → web
│ ⚙ Brain URL · Device ID │
└─────────────────────────┘
```

**Out of scope for Flutter (use web):**

- Multi-message chat thread, SSE streaming UI, session sidebar, glass/marketing layout experiments, “settings” beyond brain URL + device identity.

---

## Android

**Do not reimplement the device bridge in Flutter.** Use `clients/android/` (Kotlin `BridgeService`) for `android_open` / `tool_execute`. Flutter on Android, if ever shipped, should be Field-only + link to web — separate ADR required.

## Technical focus

| Layer | Field Body responsibility |
|-------|-------------------------|
| L1 | `device_id`, token, brain URL |
| L2 | `/pair`, `/health`; WS register, `tool_execute` / `tool_result` (confirm WS → ISSUE-104) |
| L3 | Pending queue, execution handlers, reconnect policy |
| L4 | Confirmation cards, action log glance, link-out to web |

Existing `ChatController` + chat shell in `clients/flutter/` are **legacy spike** — migrate toward Field screens; do not add chat features here until explicitly re-scoped.

---

## Issues and lanes

- New Flutter work: lane **`clients/flutter/**`** + acceptance must cite **Field Body** capability (bridge, tool, confirm), not “chat parity with web.”
- Design: minimal Material; [DESIGN.md](../DESIGN.md) anti-duplication still applies (one status zone, no fake “Jarvis Web” clone).

---

## Verify

```bash
cd clients/flutter
flutter pub get
flutter analyze
# Manual: brain up, app registers, simulate tool_execute / confirm_request (when implemented)
```

Related: [FLUTTER_LAYERS.md](FLUTTER_LAYERS.md) · [FLUTTER_UI.md](FLUTTER_UI.md) (breakpoints only if a thin UI remains) · [OSS.md](../OSS.md)
