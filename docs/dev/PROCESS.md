# Development process — feedback loop

**Doc map:** [DOCS_MAP.md](../DOCS_MAP.md)

This is the **internal AI of app development** for Jarvis: deterministic orchestration + coding agents.

**Two people or two AIs can work at the same time** — see [PARALLEL.md](PARALLEL.md).

Typical pair: **Cursor** + **Google Antigravity** or **MiniMax** (sometimes **Claude Sonnet** as the other agent).

## Loop

```text
sync / loop → brief --owner ME → claim --owner ME → implement → verify → update/done → sync
```

**Dynamic instructions (not static):** `python scripts/devloop.py brief --owner YOUR_ID` writes [docs/board/LIVE_BRIEF.md](../board/LIVE_BRIEF.md) from live issues + inbox + lanes.  
**Shared plan:** `python scripts/devloop.py sync` refreshes NOW/NEXT and [docs/board/LIVE_PLAN.md](../board/LIVE_PLAN.md).  
Shortcut: `python scripts/sync_workspace.py minimax`

## Commands

```bash
python scripts/devloop.py bootstrap
python scripts/devloop.py status
python scripts/devloop.py sync --owner cursor
python scripts/devloop.py brief --owner antigravity
python scripts/devloop.py plan
python scripts/devloop.py loop
python scripts/devloop.py next --owner cursor
python scripts/devloop.py next --owner minimax2 --tier mini
python scripts/devloop.py verify ISSUE-00N   # lane paths exist
python scripts/devloop.py claim ISSUE-00N --owner cursor
python scripts/devloop.py release ISSUE-00N --owner cursor
python scripts/devloop.py update ISSUE-00N --note "..."
python scripts/devloop.py done ISSUE-00N
python scripts/devloop.py issue --title "..." --phase 0 --priority P1
python scripts/devloop.py refresh
```

## Verify doc links

```bash
python scripts/verify_doc_links.py    # from repo root; exits 0 if README/AGENTS/docs/dev links resolve
```

## Rules

1. **Max 2 NOW issues** — one per worker (person or AI)
2. Always pass **`--owner`** (`cursor`, `antigravity`, `claude`, …)
3. Do not mark done without [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)
4. Progress notes via `update` so the other worker can see handoff
5. `refresh` never invents scope; it ranks open issues from frontmatter
6. Stay in your lane — [PARALLEL.md](PARALLEL.md)
7. Environment — [DEV_ENV.md](DEV_ENV.md) · `check_dev_env.py` · `dev_up.ps1` (Windows)
8. Issue `status: todo` is treated like `backlog` for `next` / LIVE_PLAN ordering

## Dual-agent handoff (Cursor + Antigravity / Claude)

Use the **feedback bus** every session:

```bash
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner ME
python scripts/devloop.py say --from ME --to THEM --kind note -- "…"
```

1. Worker A: `claim ISSUE-010 --owner cursor` then implements brain (auto-posts claim)
2. Worker B: `inbox --owner antigravity` → claim a non-overlapping issue
3. Each runs `brief --owner ME` (writes LIVE_BRIEF; includes inbox)
4. `done` auto-posts handoff with next tip
5. Neither steals the other's claim without `--steal`

Protocol: [FEEDBACK_LOOP.md](FEEDBACK_LOOP.md)
Ensure you kill existing UI processes before launching new ones to avoid multiple instances.
