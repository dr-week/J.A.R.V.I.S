---
id: ISSUE-071
title: Example third-party connector using SDK
status: done
priority: P1
phase: 6
labels: [sdk, integrations]
owner: minimax
claimed_at: 2026-08-08T19:17:41Z
blocked_by: [ISSUE-070]
acceptance:
  - One real connector built only via SDK/template
  - Documented in CHANGELOG
---

## Context

Prove expandability.

## Notes

- [2026-08-09T15:35:49Z] Marked done


- Claimed by minimax at 2026-08-08T19:17:41Z
- Claimed by minimax at 2026-08-08T19:14:55Z
- [2026-08-09T16:30Z] Weather connector plugin (`backend/plugins/weather`) verified:
  loads via `discover_plugins()`, registers `weather_current` + `weather_forecast`
  (both `risk=auto`, `executor=brain`). Live Open-Meteo calls returned real data
  (London current, Paris 2-day forecast). Documented in CHANGELOG. Done.
