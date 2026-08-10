# Contributing

## Humans (including pair / 2-person)

1. Pick a stable owner id (`alice`, `bob`, …).
2. See [docs/dev/PARALLEL.md](docs/dev/PARALLEL.md) if someone else is also working.
3. Pick work from the board or create an issue:

```bash
python scripts/devloop.py issue --title "..." --phase 0 --priority P1
python scripts/devloop.py next --owner alice
python scripts/devloop.py claim ISSUE-00N --owner alice
```

4. Implement against acceptance criteria.
5. Finish or free the slot:

```bash
python scripts/devloop.py done ISSUE-00N
# or
python scripts/devloop.py release ISSUE-00N --owner alice
python scripts/devloop.py refresh
```

**Max 2 NOW issues** — one per person/AI.

## Agents

Follow [AGENTS.md](AGENTS.md). Always pass `--owner`:

```bash
python scripts/devloop.py prompt --owner cursor
python scripts/devloop.py prompt --owner antigravity
python scripts/devloop.py prompt --owner claude
```

Owner ids: `cursor` (this IDE), `antigravity` (Google Antigravity), `claude` (Claude Sonnet when that is the other agent).
## Docs are source of truth

- Product: `docs/REQUIREMENTS.md`, `docs/SCOPE.md`, `docs/ARCHITECTURE.md`
- Process: `docs/dev/PROCESS.md`, `docs/dev/PARALLEL.md`
- Living state: `docs/board/*`

If code and docs disagree, **fix docs or open an ADR** in `docs/DECISIONS.md`.

## Pull requests / commits

- One issue per change when possible
- Reference `ISSUE-XXX` and owner in the commit message when useful
- Do not commit `.env`, keys, or personal memory dumps
- Prefer separate dirs/branches when two workers run in parallel
