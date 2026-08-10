# Acceptance

## Issue-level

An issue is done only if:

1. Every item under its `acceptance:` list is true
2. No SCOPE violations introduced
3. Security rules respected (no leaked secrets)
4. Board updated via `devloop done`
5. If architecture changed, an ADR was appended

## Phase-level

A phase is done when all of its P0 issues are `done` and ROADMAP exit criteria are met.

## Product smoke checks (later phases)

| Phase | Smoke |
|-------|-------|
| 0 | Message round-trip phone/PC ↔ brain |
| 1 | Memory set on A, recalled on B |
| 2 | Tool action + audit log entry |
| 3 | ≥3 domain tools pass sample asks |
| 4 | Voice turn succeeds on one client |
| 5 | Home scene + cross-room/phone continuity |
| 6 | New plugin added using SDK docs only |

## Agent self-check before claiming done

- [ ] Re-read issue acceptance
- [ ] DESIGN.md anti-duplication rules satisfied (UI issues touching `clients/**`)
- [ ] Surface UI doc updated if layout/chrome changed ([WEB_UI](dev/WEB_UI.md), [FLUTTER_UI](dev/FLUTTER_UI.md), [MINIMAX_UI](dev/MINIMAX_UI.md))
- [ ] Ran relevant commands / tests noted in issue
- [ ] Updated docs if user-facing behavior changed
- [ ] `python scripts/devloop.py done ISSUE-XXX`