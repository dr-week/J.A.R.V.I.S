---
id: ISSUE-113
title: Wire JarvisApp to FieldController and FieldHome
status: done
priority: P1
phase: 2
labels: [flutter, starter]
owner: minimax
claimed_at: 2026-08-09T19:05:00Z
blocked_by: [ISSUE-112]
acceptance:
  - jarvis_app.dart provides FieldController and home FieldScreen
  - ChatScreen not default route (chat files remain until ISSUE-103)
  - flutter analyze passes on touched files
---

## Context

Completes default app shell for **ISSUE-101**.

## Lane

- `clients/flutter/lib/app/jarvis_app.dart`

## Work

- [x] FieldController + FieldScreen as MaterialApp home

## Notes

- Done 2026-08-10.
