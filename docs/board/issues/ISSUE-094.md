---
id: ISSUE-094
title: Flutter device bridge WebSocket status
status: done
priority: P2
phase: 2
labels: [flutter, starter]
owner: antigravity
claimed_at: 2026-08-09T05:54:53Z
blocked_by: []
acceptance:
  - Optional bridge mode connects to brain /ws and registers device_id
  - Footer bridge line shows connected / reconnecting like Windows Flet
  - tool_execute not required in v1 — register + ping/pong only OK
---

## Lane

- `clients/flutter/lib/data/bridge_client.dart` (new)
- `clients/flutter/lib/state/chat_controller.dart`

See [FLUTTER_LAYERS.md](../../dev/FLUTTER_LAYERS.md) phase C.

## Notes

- [2026-08-09T05:56:20Z] Marked done


- Claimed by antigravity at 2026-08-09T05:54:53Z
