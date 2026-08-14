---
name: jarvis-dev
description: How to develop the Jarvis repo using the board and devloop. Use for issue-driven work with Cursor, Google Antigravity, or Claude Sonnet as parallel workers.
---

# Jarvis development skill

**Doc map:** [docs/DOCS_MAP.md](../docs/DOCS_MAP.md)  
**Blackbox / MiniMax:** [docs/dev/MINIMAX.md](../docs/dev/MINIMAX.md) · mirror [.blackbox/skills/jarvis-dev/SKILL.md](../.blackbox/skills/jarvis-dev/SKILL.md)  
**Ministral mini coder:** [docs/dev/MINISTRAL.md](../docs/dev/MINISTRAL.md) · [MINISTRAL_QUEUE.md](../docs/dev/MINISTRAL_QUEUE.md)

## Required reading order

1. `AGENTS.md`
2. `docs/SCOPE.md`
3. `docs/board/NOW.md` and [LIVE_PLAN.md](../docs/board/LIVE_PLAN.md) (after `devloop sync`)
4. [AI_CODE_STRUCTURE.md](../docs/dev/AI_CODE_STRUCTURE.md) when touching code layout
4b. [MODULARITY_PLAN.md](../docs/dev/MODULARITY_PLAN.md) when splitting modules or `devloop` (**117–118**)
5. [AI_CODER_AUTOMATION.md](../docs/dev/AI_CODER_AUTOMATION.md) — gates before `done`
6. Target `docs/board/issues/ISSUE-XXX.md`
7. `docs/dev/DEFINITION_OF_DONE.md`
8. **UI lane:** [DESIGN.md](../docs/DESIGN.md) + [WEB_UI](../docs/dev/WEB_UI.md) (chat) or [FLUTTER_FIELD](../docs/dev/FLUTTER_FIELD.md) (Field) or [MINIMAX_UI](../docs/dev/MINIMAX_UI.md) (Windows)

```bash
python scripts/devloop.py sync --owner YOUR_ID
python scripts/devloop.py brief --owner YOUR_ID
python scripts/devloop.py status
python scripts/devloop.py next --owner YOUR_ID
python scripts/devloop.py claim ISSUE-XXX --owner YOUR_ID
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner YOUR_ID
python scripts/devloop.py say --from YOUR_ID --to OTHER --kind note -- "message"
python scripts/devloop.py update ISSUE-XXX --note "progress"
python scripts/devloop.py done ISSUE-XXX
python scripts/devloop.py release ISSUE-XXX --owner YOUR_ID
python scripts/devloop.py refresh
```

Generated files: `docs/board/LIVE_PLAN.md`, `docs/board/LIVE_BRIEF.md` (use `brief` / `sync`, not static `prompt` text).

## Rules

- **Two workers max** in NOW (person or AI) — see `docs/dev/PARALLEL.md`
- Start every session with `devloop loop` + `inbox --owner ME` — see `docs/dev/FEEDBACK_LOOP.md`
- One issue per `--owner` at a time
- Do not start Phase N product code while prior phase P0s are open (unless issue says otherwise)
- Append ADRs to `docs/DECISIONS.md` for architecture choices
- **Zero-Code OSS Rule:** Prefer 3-line PyPI wrappers, CLI subprocesses, Docker sidecars, or MCP servers over custom Python/JS implementations (see `docs/OSS.md`).
- **Backend OSS lane:** Read `docs/dev/BACKEND_OSS_PLAN.md` before adding infrastructure. Keep adapters isolated under `backend/plugins/`, preserve API contracts, and add a contract test plus ADR for each new backend service.
- **Chained verification:** Run `python scripts/verify_backend.py` before handoff; it chains the OSS gate, compile check, and focused backend tests.
- **Release verification:** Run `python scripts/verify_backend.py --full` before release or broad backend changes.
- Never commit secrets
- Do not edit another owner's claimed lane without Notes coordination

**MiniMax (Blackbox):** full agent contract in [docs/dev/MINIMAX.md](../docs/dev/MINIMAX.md).

## Output expectations

- Code or docs matching acceptance
- Board updated
- Short note of what changed
