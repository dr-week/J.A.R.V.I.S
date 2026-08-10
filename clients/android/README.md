# Android client — device bridge (ISSUE-012 / 033)

Kotlin + Jetpack Compose. **Chat UI is not the long-term product here** — use **[clients/web](../web/)** (Vite) for conversations. This app proves **pairing, SSE chat stub, and `android_open` bridge** ([PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md)).

## Requirements

- Android Studio Ladybug+ (or SDK 35 + JDK 17)
- Brain running on your PC: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787`

## Open & run

1. Open folder `clients/android` in Android Studio (Gradle sync).
2. Run on emulator or physical device.
3. Set **Brain URL**:
   - Emulator → `http://10.0.2.2:8787` (default)
   - Real phone on same Wi‑Fi → `http://<your-pc-lan-ip>:8787`

## Acceptance

- [x] App sends a message to brain (`POST /chat` SSE)
- [x] Displays streamed reply
- [x] Brain base URL is editable and persisted
- [x] Brain can dispatch `android_open` launch; result returned and logged

## Device bridge (ISSUE-033)

The app runs a background `BridgeService` that connects to the brain over the
same WebSocket (`/ws`) the Windows client uses, so the brain can remotely
trigger **intent / deep-link launches** on this phone.

- Registers with a persistent device id (`android-<id>`) and handles
  `tool_execute` for the **`android_open`** tool.
- `target` handling:
  - `https://…` / `market://…` → `ACTION_VIEW` intent
  - app package name (e.g. `com.google.android.youtube`) → launch / store
- Replies `tool_result` with the matching `request_id`; the brain writes the
  outcome to `action_log`.
- Auto-starts from `MainActivity` and reconnects with backoff while running.

Bridge status text is shown at the top of the chat screen.

Parity reference: [Windows client README](../windows/README.md) (device bridge, tray, pairing, `kill_stale.ps1`).

## Notes

- Cleartext HTTP allowed for LAN dev (`usesCleartextTraffic`)
- Device id + session id generated locally
- Pairing token (ISSUE-013) can be added later; Windows client already has `/pair` stub
