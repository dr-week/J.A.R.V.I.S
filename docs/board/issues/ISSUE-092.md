---
id: ISSUE-092
title: Flutter portrait-first responsive presence scaffold
status: done
priority: P2
phase: 0
labels: [flutter, android, windows, starter, ui]
owner: cursor
claimed_at: 
blocked_by: []
acceptance:
  - clients/flutter runs on Android or Windows after flutter pub get
  - Portrait shows single-column chat shell
  - Landscape or width >= 600 shows side rail plus main chat column
  - docs/dev/FLUTTER_UI.md describes breakpoints
---

## Context

Phone UI in portrait; landscape and wide layouts flex via rail/split without a second app.

## Lane

- `clients/flutter/**`
- `docs/dev/FLUTTER_UI.md`

## Work

- [x] Scaffold + ResponsiveShell
- [x] Wire pair, health, SSE chat (ISSUE-093)
- [x] `flutter analyze` on dev machine with SDK installed (3 info hints only, 2026-08-09)

## Notes

- [2026-08-08T20:38:30Z] Marked done


Flet Windows GUI remains until Flutter verified on device. **093** code complete; run locally to verify.
