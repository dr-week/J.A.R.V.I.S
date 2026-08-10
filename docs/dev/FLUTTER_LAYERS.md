# Flutter client — stratified layers (ISSUE-092 / 093)

Build bottom-up. Each layer only depends on layers below.

```text
┌─────────────────────────────────────────┐
│  L4 UI — chat_screen, responsive_shell  │
├─────────────────────────────────────────┤
│  L3 State — ChatController (ChangeNotifier)│
├─────────────────────────────────────────┤
│  L2 Data — BrainApi (pair, health, SSE) │
├─────────────────────────────────────────┤
│  L1 Core — BrainConfig, TokenStore      │
└─────────────────────────────────────────┘
         │ HTTP/SSE → FastAPI brain
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| **L1** | `lib/core/` | URLs, device id, persisted token + brain URL |
| **L2** | `lib/data/brain_api.dart`, `lib/data/bridge_client.dart` | `/pair`, `/health`, `/chat` SSE; `/ws` bridge |
| **L3** | `lib/state/chat_controller.dart` | Messages, session id, connect/pair/send |
| **L4** | `lib/ui/` | Portrait-first shell; no HTTP in widgets |

**Phase gates**

| Phase | Issue | Exit |
|-------|-------|------|
| A | 092 | Responsive shell + placeholder |
| B | 093 | L1–L4 wired; real chat stream |
| C | 094 | WebSocket bridge + rail status |
| D | — | Deprecate Flet GUI |

See [FLUTTER_UI.md](FLUTTER_UI.md) for breakpoints.
