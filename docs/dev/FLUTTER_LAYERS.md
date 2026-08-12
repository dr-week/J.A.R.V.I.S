# Flutter client — stratified layers (ISSUE-092 / 093)

Build bottom-up. Each layer only depends on layers below.

```text
┌─────────────────────────────────────────┐
│  L4 UI — field_screen                   │
├─────────────────────────────────────────┤
│  L3 State — FieldController (ChangeNotifier) │
├─────────────────────────────────────────┤
│  L2 Data — BrainApi (pair, health), BridgeClient │
├─────────────────────────────────────────┤
│  L1 Core — BrainConfig, TokenStore      │
└─────────────────────────────────────────┘
         │ HTTP/WS → FastAPI brain
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| **L1** | `lib/core/` | URLs, device id, persisted token + brain URL |
| **L2** | `lib/data/brain_api.dart`, `lib/data/bridge_client.dart` | `/pair`, `/health`; `/ws` bridge |
| **L3** | `lib/state/field_controller.dart` | Bridge state, pending actions, connect/pair |
| **L4** | `lib/ui/` | Field screen; no HTTP in widgets |

**Phase gates**

| Phase | Issue | Exit |
|-------|-------|------|
| A | 092 | Responsive shell + placeholder |
| B | 093 | L1–L4 wired; real chat stream |
| C | 094 | WebSocket bridge + rail status |
| D | — | Deprecate Flet GUI |

See [FLUTTER_UI.md](FLUTTER_UI.md) for breakpoints.
