# Presence clients — one chat app, different jobs

**Rule:** The **chat product** (threads, sessions, settings, design) lives in **`clients/web/`** (Vite + TypeScript) only. Other clients must **not** rebuild that app.

| Client | Stack | Path | Purpose |
|--------|-------|------|---------|
| **Chat + product UI** | Vite + React + TS | `clients/web/` | The assistant you sit with at a screen |
| **Field Body (mobile)** | Flutter + Dart | `clients/flutter/` | Pocket **bridge + tools + confirmations** — see [FLUTTER_FIELD.md](FLUTTER_FIELD.md) |
| **Android Presence** | Kotlin + Compose | `clients/android/` | Native **pair + `android_open` + confirm UI** + open web; not chat product |
| **Windows agent** | Flet + Python | `clients/windows/` | Tray, voice, wake-word, `tool_execute` on PC — not a second chat UI |

Brain: `backend/` (FastAPI).

---

## Desktop Install (Web PWA)

To use Jarvis as a standalone desktop app on Windows/Mac/Linux, install the **Web** client as a PWA or desktop shortcut:
1. Open `http://localhost:5173` (or your production URL) in Edge or Chrome.
2. **Edge**: Click the "App available. Install Jarvis" icon in the address bar, or go to `Settings and more (...) > Apps > Install this site as an app`.
3. **Chrome**: Click the "Install" icon in the address bar, or go to `Menu > Save and share > Install page as app...`.

This gives you a borderless window, taskbar icon, and standard app lifecycle for the chat product.

---

## Flutter ≠ chat

Flutter is **Jarvis Field**: register device, run `executor: "client"` tools, approve confirmations (**after ISSUE-104**), show glance status, link out to web for full chat.

**Forbidden in Flutter without ADR:** session list, SSE chat thread, composer parity, sidebar/settings clone of web.

---

## Agent routing

| Task | Work in | Doc |
|------|---------|-----|
| Chat, design, sessions, settings | `clients/web/**` | [WEB_UI.md](WEB_UI.md) |
| Cross-platform Field (bridge/confirm) | `clients/flutter/**` | [FLUTTER_FIELD.md](FLUTTER_FIELD.md) |
| Native Android intents / Presence UI | `clients/android/**` | [clients/android/README.md](../../clients/android/README.md) |
| Tray, voice, Windows open | `clients/windows/**` | [MINIMAX_UI.md](MINIMAX_UI.md) + README |

Default UI issues → **web**.

---

## Run

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787
cd clients/web && npm run dev
```

Related: [DESIGN.md](../DESIGN.md) · [OSS.md](../OSS.md) · [DECISIONS.md](../DECISIONS.md) ADR-0023
