# LIVE BRIEF (generated — do not edit)

_Generated: 2026-08-09T20:20:43Z UTC · owner `cursor` · issue `ISSUE-115` · `5fcccd3034f9`_

Regenerate: `python scripts/devloop.py brief --owner cursor`

## Situation (this run)

- Board fingerprint `5fcccd3034f9` — if unchanged, another agent may have stale chat context; re-run `sync`.
- Focus phase **2**: Hands — tools, device bridges, audit
- NOW occupied: ISSUE-101=minimax

## Your assignment

### ISSUE-115: Pytest Integration

| Field | Value |
|-------|-------|
| phase | 0 |
| priority | P1 |
| status | backlog |
| claimed owner | — |
| file | `docs\board\issues\ISSUE-115.md` |

- blocked_by (must be done): ['ISSUE-119']

### Acceptance (verify each before `done`)

- [ ] pytest and pytest-asyncio in pyproject.toml dev optional-deps
- [ ] backend/tests/test_brain.py exists and passes with pytest
- [ ] Document run command in backend/README.md or DEV_ENV.md

### Lane

- See PARALLEL.md
- **Prefer paths:** `paths in issue acceptance`
- **Avoid paths:** `other worker NOW paths`

### Owner rules

- Owner id for devloop: `cursor`
- Session: `devloop loop` -> `inbox --owner cursor` -> claim -> brief/prompt -> done -> say
- Integration + review; Soul/Hands core when bridges stable
- Pair with minimax on 033 or antigravity on soul/sync lanes

### Inbox (messages to you)

- [2026-08-09T15:43:20Z] **antigravity** `done` ISSUE-100: Done ISSUE-100: None. Slot free. Suggested next tip: none. Run: python scripts/devloop.py loop
- [2026-08-09T16:12:39Z] **antigravity** `claim` ISSUE-102: Claimed ISSUE-102: Web — session list and resume from brain. Please avoid overlapping paths.
- [2026-08-09T16:14:59Z] **unknown** `done` ISSUE-102: Done ISSUE-102: Web — session list and resume (FR-P3). Slot free. Suggested next tip: ISSUE-101. Run: python scripts/devloop.py loop
- [2026-08-09T17:48:38Z] **minimax** `claim` ISSUE-101: Claimed ISSUE-101: Flutter Field Body — desktop bridge shell and tool_execute. Please avoid overlapping paths.
- [2026-08-09T17:50:48Z] **antigravity** `claim` ISSUE-105: Claimed ISSUE-105: Web UI verification — 098/099 acceptance and DESIGN header. Please avoid overlapping paths.
- [2026-08-09T17:51:14Z] **antigravity** `done` ISSUE-105: Done ISSUE-105: Web UI verification — 098/099 acceptance and DESIGN header. Slot free. Suggested next tip: ISSUE-101. Run: python scripts/devloop.py loop
- [2026-08-09T18:43:43Z] **antigravity** `claim` ISSUE-104: Claimed ISSUE-104: Backend — WS confirm_request when tool gate blocks. Please avoid overlapping paths.
- [2026-08-09T18:44:11Z] **antigravity** `done` ISSUE-104: Done ISSUE-104: Backend — WS confirm_request when tool gate blocks. Slot free. Suggested next tip: ISSUE-101. Run: python scripts/devloop.py loop

### Required reads (issue-specific)

- `AGENTS.md`
- `docs/SCOPE.md`
- `docs/board/issues/ISSUE-115.md`
- `docs/dev/PARALLEL.md`
- `docs/dev/DEFINITION_OF_DONE.md`

### Issue notes / body

## Context

Replace scratch tests with pytest. **Mini slice:** do deps + one test file only.

[MINIMAX_QUEUE.md](../../dev/MINIMAX_QUEUE.md) wave X · [STRATEGY_FORWARD.md](../../dev/STRATEGY_FORWARD.md)

## Lane

- `pyproject.toml`
- `backend/tests/**`

## Work

- [ ] Add pytest + pytest-asyncio to pyproject.toml `[project.optional-dependencies] dev`
- [ ] Move or recreate `test_brain.py` under `backend/tests/`
- [ ] `pytest backend/tests` passes from repo root

## Notes

Created by devloop. Prefer `uv run pytest` if uv installed; else `pip install -e ".[dev]"`.

### Finish

```bash
python scripts/devloop.py update ISSUE-115 --note "verified: ..."
python scripts/devloop.py done ISSUE-115
python scripts/devloop.py say --from cursor --to cursor --kind done --issue ISSUE-115 -- "summary"
python scripts/devloop.py sync
```
