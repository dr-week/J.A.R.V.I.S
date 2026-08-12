# LIVE BRIEF (generated — do not edit)

_Generated: 2026-08-11T18:26:47Z UTC · owner `cursor` · issue `ISSUE-147` · `cda35d9f87b1`_

Regenerate: `python scripts/devloop.py brief --owner cursor`

## Situation (this run)

- Board fingerprint `cda35d9f87b1` — if unchanged, another agent may have stale chat context; re-run `sync`.
- Focus phase **2**: Hands — tools, device bridges, audit
- NOW occupied: none

## Your assignment

### ISSUE-147: M1 Phase 2 exit proof — multi-step Windows action + audit log

| Field | Value |
|-------|-------|
| phase | 2 |
| priority | P0 |
| status | backlog |
| claimed owner | — |
| file | `docs\board\issues\ISSUE-147.md` |

### Acceptance (verify each before `done`)

- [ ] Scripted or documented multi-step tool run on Windows bridge with action_log entries
- [ ] Phase 2 exit note updated in ROADMAP (Windows path met)
- [ ] Android gap called out as follow-up (not blocking Windows exit)

### Lane

- Windows lane only
- **Prefer paths:** `clients/windows/`
- **Avoid paths:** `clients/android/`

### Owner rules

- Owner id for devloop: `cursor`
- Session: `devloop loop` -> `inbox --owner cursor` -> claim -> brief/prompt -> done -> say
- Integration + review; Soul/Hands core when bridges stable
- Pair with minimax on 033 or antigravity on soul/sync lanes

### Inbox (messages to you)

- [2026-08-11T17:54:18Z] **unknown** `done` ISSUE-126: Done ISSUE-126: Prototype openwakeword wake listener. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:54:44Z] **unknown** `done` ISSUE-129: Done ISSUE-129: Implement Embedded Lua Engine. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:55:01Z] **unknown** `done` ISSUE-133: Done ISSUE-133: R subprocess plugin template. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:55:04Z] **unknown** `done` ISSUE-103: Done ISSUE-103: Flutter — strip legacy chat UI; Field home only. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:55:12Z] **unknown** `done` ISSUE-107: Done ISSUE-107: WebSocket /ws authenticate device token. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:56:29Z] **unknown** `done` ISSUE-142: Done ISSUE-142: Flutter Field — handle WS confirm_request and approve/deny. Slot free. Suggested next tip: ISSUE-120. Run: python scripts/devloop.py loop
- [2026-08-11T17:57:34Z] **subagent** `done` ISSUE-120: Done ISSUE-120: GitHub Action dev-smoke workflow. Slot free. Suggested next tip: ISSUE-131. Run: python scripts/devloop.py loop
- [2026-08-11T17:57:36Z] **unknown** `done` ISSUE-131: Done ISSUE-131: Create velocity_build Tool. Slot free. Suggested next tip: ISSUE-132. Run: python scripts/devloop.py loop

### Required reads (issue-specific)

- `AGENTS.md`
- `docs/SCOPE.md`
- `docs/board/issues/ISSUE-147.md`
- `docs/SYNC_PROTOCOL.md`
- `clients/windows/README.md`
- `docs/TOOL_SCHEMA.md`
- `docs/dev/PARALLEL.md`
- `docs/dev/DEFINITION_OF_DONE.md`

### Issue notes / body

## Context

Plan: [MAJOR_WORK_PLAN.md](../../dev/MAJOR_WORK_PLAN.md) **M1**. Owner: **cursor** (not web).

## Lane

- `clients/windows/**`
- `backend/app/hands/**`
- `backend/app/api/hands.py`
- `docs/ROADMAP.md`
- `scripts/` (one proof script if added)

## Work

- [ ] Multi-step Windows tool path + action_log proof
- [ ] ROADMAP Phase 2 exit note
- [ ] Note Android follow-up

## Notes

Created from MAJOR_WORK_PLAN M1

### Finish

```bash
python scripts/devloop.py update ISSUE-147 --note "verified: ..."
python scripts/devloop.py done ISSUE-147
python scripts/devloop.py say --from cursor --to cursor --kind done --issue ISSUE-147 -- "summary"
python scripts/devloop.py sync
```
