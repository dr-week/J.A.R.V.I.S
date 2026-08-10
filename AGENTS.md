# AGENTS.md — Coding agent contract

This file is the primary operating manual for **Cursor, Google Antigravity, Claude Sonnet**, and any other coding agent (Blackbox/MiniMax optional).

## Mission

Build **Jarvis**: a close personal assistant that:

- Knows the user (Soul)
- Executes real actions (Hands)
- Lives on phone, PC, and in the house (Presence + House body)
- Uses one centralized synced brain

Examples like tasks/reminders/contacts are **proof of execution**, not the product ceiling.

We co-build with the human for a shared better future — roles and economic realism: [docs/PARTNERSHIP.md](docs/PARTNERSHIP.md).

**Blackbox MiniMax:** follow [docs/dev/MINIMAX.md](docs/dev/MINIMAX.md); owner id `minimax`.

**Doc sync hub:** [docs/DOCS_MAP.md](docs/DOCS_MAP.md) — update mirrored files together (skills, MINIMAX, `.blackbox/RULES.md`).

## Before you write code

1. Read [docs/SCOPE.md](docs/SCOPE.md) — stay in scope
2. Read [docs/board/NOW.md](docs/board/NOW.md) — max **2** parallel workers
3. Read [docs/dev/PARALLEL.md](docs/dev/PARALLEL.md) if another person/AI is active
4. Read the issue file under [docs/board/issues/](docs/board/issues/)
5. Run with **your owner id**:

```bash
python scripts/devloop.py next --owner YOUR_ID
python scripts/devloop.py claim ISSUE-XXX --owner YOUR_ID
python scripts/devloop.py prompt --owner YOUR_ID
```

6. Follow acceptance criteria in the issue + [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md)
7. **UI / Presence:** [PRESENCE_STACKS.md](docs/dev/PRESENCE_STACKS.md) · [DEV_ENV.md](docs/dev/DEV_ENV.md) · mini tasks [MINIMAX_QUEUE.md](docs/dev/MINIMAX_QUEUE.md)

**Cross-agent bus (Cursor ↔ Antigravity ↔ MiniMax ↔ Claude):**

```bash
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner YOUR_ID
python scripts/devloop.py say --from YOUR_ID --to OTHER_ID --kind note -- "message"
```

See [docs/dev/FEEDBACK_LOOP.md](docs/dev/FEEDBACK_LOOP.md).

## Agent factory

Read [docs/dev/AI_CODER_AUTOMATION.md](docs/dev/AI_CODER_AUTOMATION.md) for test gates, scope, and coder≠reviewer before `devloop done`.

## Hard rules

- **Do not launch multiple UI instances.** Always check `manage_task list` (or kill existing processes) before running `flutter run` or `python client.py` as a background daemon. Kill stale instances first.
- Do **not** invent features outside [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) / [docs/SCOPE.md](docs/SCOPE.md)
- Prefer smallest vertical slice that meets acceptance
- API keys only in `.env` (never commit secrets); see [docs/SECURITY.md](docs/SECURITY.md)
- Append architecture choices to [docs/DECISIONS.md](docs/DECISIONS.md)
- Update the board via `devloop` (`claim`, `update`, `done`, `release`, `refresh`)
- Keep persona consistent with [docs/PERSONA.md](docs/PERSONA.md) when touching assistant behavior
- **Do not edit another worker's claimed issue files/paths** without coordinating in Notes

## Parallel work (2 people or 2 AIs)

Supported by design. Each worker:

1. Picks a stable `--owner` id (`cursor`, `antigravity`, `claude`, `minimax`, …)
2. Claims at most **one** NOW issue
3. Uses lane pairs in [docs/dev/PARALLEL.md](docs/dev/PARALLEL.md) (e.g. Windows vs Android clients)

## Work loop

```text
devloop refresh → next --owner ME → claim --owner ME → implement → verify → done → refresh
```

Details: [docs/dev/PROCESS.md](docs/dev/PROCESS.md)

> [!WARNING] 
> **Devloop Monolith Alert**: `scripts/devloop.py` is currently a massive 40KB legacy script. Do not attempt to refactor or rewrite it in a single pass. A formal technical debt Epic has been scheduled in `ROADMAP.md` to decompose it into a Typer/Pydantic modular architecture. Until then, make only isolated bug fixes.

## Coding Style (AI-Friendly)

Write code that is easy for small-context AIs (like MiniMax) to read and fix:
1. **Small Files:** Keep modules short. Do not create massive monolithic files.
2. **Clear Comments:** Write explicit docstrings explaining *why* something is done.
3. **Flat Logic:** Avoid deeply nested `if/else`. Return early.
4. **Isolate Changes:** Keep bug fixes isolated to the smallest scope possible.

## Skills

- [skills/jarvis-dev/SKILL.md](skills/jarvis-dev/SKILL.md) — how to develop this repo
- [skills/jarvis-product/SKILL.md](skills/jarvis-product/SKILL.md) — product constraints
- [.blackbox/skills/](.blackbox/skills/) — Blackbox mirrors (see [docs/DOCS_MAP.md](docs/DOCS_MAP.md))
- [docs/dev/MINIMAX.md](docs/dev/MINIMAX.md) — MiniMax-only rules
- [.blackbox/RULES.md](.blackbox/RULES.md) — MiniMax entrypoint

## Repo map

| Path | When it exists | Role |
|------|----------------|------|
| `docs/` | now | Specs and board |
| `docs/DOCS_MAP.md` | now | Doc clusters + sync checklist |
| `scripts/devloop.py` | now | Build feedback loop |
| `backend/` | Phase 0+ | Central brain (FastAPI) — see `backend/app/README.md` |
| `clients/android/` | Phase 0+ | Phone presence (Kotlin Compose stub) |
| `clients/windows/` | Phase 0+ | Desktop presence (Flet; migrating to Flutter) |
| `clients/flutter/` | Phase 0+ | Phone-first Flutter UI (portrait default, adaptive landscape) |
| `clients/house/` | Phase 5 | Room satellites |
| `tools/` | Phase 2+ | Executable plugins |

## Phase gate

Do not start Phase **N** product code until the board shows prior phase P0 issues `done` (or NOW explicitly says otherwise).

Current phase focus: see [docs/board/NOW.md](docs/board/NOW.md) and [docs/ROADMAP.md](docs/ROADMAP.md).

## Definition of done

See [docs/dev/DEFINITION_OF_DONE.md](docs/dev/DEFINITION_OF_DONE.md). Minimum:

- Acceptance checklist checked
- Docs/board updated if behavior or API changed
- `python scripts/devloop.py done ISSUE-XXX` run
