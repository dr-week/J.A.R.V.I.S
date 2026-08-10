---
id: ISSUE-093
title: Flutter brain pair health and SSE chat
status: done
priority: P2
phase: 0
labels: [flutter, android, starter, ui]
owner: cursor
claimed_at: 
blocked_by: []
acceptance:
  - Pair with POST /pair and persist token via shared_preferences
  - GET /health updates status and assistant name
  - POST /chat streams SSE into assistant bubble
  - Portrait and landscape layouts unchanged (ResponsiveShell)
---

## Context

Wire L1–L4 per [FLUTTER_LAYERS.md](../../dev/FLUTTER_LAYERS.md).

## Lane

- `clients/flutter/lib/core/**`
- `clients/flutter/lib/data/**`
- `clients/flutter/lib/state/**`
- `clients/flutter/lib/ui/**`

## Notes

- [2026-08-08T20:38:30Z] Marked done


- [2026-08-09] Implemented BrainApi, ChatController, settings dialog for brain URL.
- Verify on device: `flutter pub get && flutter run` (SDK required).
