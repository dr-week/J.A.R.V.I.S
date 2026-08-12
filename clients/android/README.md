# Android client — Presence + device bridge

Kotlin + Jetpack Compose. **Not the chat product** — conversations live in **[clients/web](../web/)**. This app is the phone **Presence / Field** body: pair, health, WebSocket bridge (`android_open` + `confirm_request`), and a button to open the full web assistant.

Stacks: [PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md) · Plan: [MAJOR_WORK_PLAN.md](../../docs/dev/MAJOR_WORK_PLAN.md) (**M-Android**)

## Requirements

- Android Studio Ladybug+ (or SDK 35 + JDK 17)
- Brain: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787`
- Pairing secret matches `JARVIS_PAIRING_SECRET` in `.env` (default often `change-me`)

## Open & run

1. Open `clients/android` in Android Studio (Gradle sync).
2. Run on emulator or device.
3. Set **Brain URL**:
   - Emulator → `http://10.0.2.2:8787`
   - Phone on Wi‑Fi → `http://<pc-lan-ip>:8787`
4. Tap **Health** → **Pair** → confirm bridge status shows connected.
5. **Open full assistant** → web chat (set web URL; emulator default `http://10.0.2.2:5173`).

## Acceptance (ISSUE-150)

- [x] Presence UI: brain URL, pairing secret, health, bridge status
- [x] `confirm_request` → Approve / Deny via `/chat` confirm phrases
- [x] Open full assistant launches web URL
- [x] DeviceBridge sends `token` on register / `?token=` query; README + plan updated

## Device bridge

`BridgeService` hosts `DeviceBridge` on `/ws`:

- Registers `android-<id>` with optional device token after `/pair`
- Handles `tool_execute` for **`android_open`** (URL or package)
- Surfaces `confirm_request` to UI via `BridgeHub`
- Reconnects with backoff; **Bridge** button restarts after re-pair

Optional **LAN smoke** box posts a one-shot `/chat` SSE ping — debug only, not product chat.

## Notes

- Cleartext HTTP allowed for LAN (`usesCleartextTraffic`)
- Flutter Field is the cross-platform twin; Kotlin owns native `android_open` intents
- Windows tray parity: [../windows/README.md](../windows/README.md)
