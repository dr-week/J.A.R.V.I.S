# Flutter Field Body — lib map

Primary chat is **web** (`clients/web/`). This app is the **Field Body**: bridge, `tool_execute`, link to web chat.

```text
lib/
├── main.dart              # Entry
├── app/jarvis_app.dart    # App widget, default route → Field
├── ui/field/              # Field screen (ship here)
├── ui/chat/               # Legacy chat — delete with ISSUE-103
├── state/field_controller.dart
├── data/bridge_client.dart, field_bridge_executor.dart, brain_api.dart
└── core/                  # theme, brain URL, tokens
```

Edit **one layer**: UI → state → data → core. Do not duplicate tool policy from `backend/app/hands/gate.py`.

See [docs/dev/FLUTTER_FIELD.md](../../docs/dev/FLUTTER_FIELD.md).
