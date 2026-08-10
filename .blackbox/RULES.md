# Blackbox / MiniMax — Jarvis rules (read first)

**Owner id:** `minimax`  
**Execute mode (no re-approve plan):** [EXECUTE.md](EXECUTE.md) — **read this if Blackbox asks for plan approval again**  
**Full rules:** [docs/dev/MINIMAX.md](../docs/dev/MINIMAX.md)  
**Windows UI mini queue:** [docs/dev/MINIMAX_UI.md](../docs/dev/MINIMAX_UI.md)  
**Doc map:** [docs/DOCS_MAP.md](../docs/DOCS_MAP.md)  
**Skills:** [.blackbox/skills/jarvis-dev/SKILL.md](skills/jarvis-dev/SKILL.md) · [jarvis-product](skills/jarvis-product/SKILL.md)

## Start every session

```bash
python scripts/devloop.py sync --owner minimax
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner minimax
python scripts/devloop.py claim ISSUE-XXX --owner minimax
python scripts/devloop.py brief --owner minimax
```

## Non-negotiable

0. **No plan re-approval** — issue + `claim` + `brief` = go. See [.blackbox/EXECUTE.md](../../.blackbox/EXECUTE.md). Implement in the same session; do not ask "approve this plan?"
1. One issue, one owner — `minimax`
2. Claim before code; `done` only when acceptance is true
3. One client lane per issue (Windows **or** Android unless issue says both)
4. Tool registry only in `backend/app/hands/registry.py`
5. Device bridge = [docs/SYNC_PROTOCOL.md](../docs/SYNC_PROTOCOL.md)
6. No secrets in git; no drive-by refactors
7. Handoff: `devloop say --from minimax --to cursor --kind done --issue ISSUE-XXX -- "summary"`

## Best at

End-to-end slices: backend + client + docs + board (see ISSUE-032).

## Next issue

Run: `python scripts/devloop.py next --owner minimax`
