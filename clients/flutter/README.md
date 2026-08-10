# Flutter presence — Field Body (experimental)

**Not the chat app.** Chat, design, sessions, and settings → **[clients/web](../web/)** (Vite + TypeScript).

This repo folder builds **Jarvis Field** — mobile pocket body: WebSocket bridge, client-tool execution, confirmation UI, link to web for full assistant.

**Spec:** [docs/dev/FLUTTER_FIELD.md](../../docs/dev/FLUTTER_FIELD.md) · [PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md)

---

## Current code (honest status)

| Piece | Status |
|-------|--------|
| Pair, health, WS register | Implemented (spike) |
| SSE chat UI | **Legacy** — do not extend; remove when Field screens land |
| `tool_execute` / `confirm_request` UI | **Backlog** — the real Flutter product |

---

## Dependencies

| Package | Role |
|---------|------|
| `provider` | State for bridge + pending confirms |
| `logging` | Debug |
| `http` / `web_socket_channel` | Brain + bridge |
| `shared_preferences` / `uuid` | Device identity |

```bash
flutter pub get
flutter analyze
flutter test
```

## Run (dev)

```bash
# Brain on LAN — emulator uses http://10.0.2.2:8787
flutter run -d <device>
```

Architecture layers: [FLUTTER_LAYERS.md](../../docs/dev/FLUTTER_LAYERS.md) (will shift toward Field Body in L3/L4).
