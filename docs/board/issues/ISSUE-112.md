---
id: ISSUE-112
title: Flutter Field home screen UI (no chat thread)
status: done
priority: P1
phase: 2
labels: [flutter, starter]
owner: minimax
claimed_at: 2026-08-09T19:05:00Z
blocked_by: []
acceptance:
  - lib/ui/field/field_screen.dart shows status, bridge line, recent actions glance
  - Uses FieldController via Provider — no ChatScreen
  - Matches layout sketch in FLUTTER_FIELD.md
---

## Context

Parent slice of **ISSUE-101**. Implemented as `field_screen.dart` (same role as planned field_home).

## Lane

- `clients/flutter/lib/ui/field/**`
- `docs/dev/FLUTTER_FIELD.md`

## Work

- [x] FieldScreen widget per FLUTTER_FIELD.md
- [x] statusLine, bridgeLine, actions from FieldController

## Notes

- Done via field_screen.dart at 2026-08-10.
