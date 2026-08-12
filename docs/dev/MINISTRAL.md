# Ministral — mini AI coder boot card

**Owner id:** `ministral` (always).  
**Role:** micro-coder only — docs, one-file fixes, single tests. Sister seat to MiniMax-mini: [MINIMAX.md](MINIMAX.md) · [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md).

**Queue:** [MINISTRAL_QUEUE.md](MINISTRAL_QUEUE.md) · PR doc slices: [01 board](pr-slices/01-board-sync.md), [04 AI-COMPANY](pr-slices/04-ai-company-docs.md) · Hub: [PR_SPLIT.md](PR_SPLIT.md)

---

## Hard caps (every turn)

| Cap | Limit |
|-----|-------|
| Files touched | **1–2** |
| Lines read | **≤120** |
| Lines written | **≤80** |
| Prefer file size | **≤200** LOC |
| Parallel issues | **0** — finish one |

## Boot order

1. [AGENTS.md](../../AGENTS.md)
2. [SCOPE.md](../SCOPE.md)
3. [NOW.md](../board/NOW.md) / [LIVE_PLAN.md](../board/LIVE_PLAN.md)
4. Target `docs/board/issues/ISSUE-XXX.md` **Lane**
5. This file

## Commands

```bash
python scripts/devloop.py sync --owner ministral
python scripts/devloop.py next --owner ministral --tier mini
python scripts/devloop.py claim ISSUE-XXX --owner ministral
python scripts/devloop.py verify ISSUE-XXX
# …implement one menu item…
python scripts/devloop.py done ISSUE-XXX --owner ministral
```

Bus: `say --from ministral --to cursor --kind note -- "…"`.

## Safe menu (pick **one**)

1. Fix one broken doc link  
2. One issue acceptance / Notes line  
3. One small pytest for an existing function  
4. One AI-COMPANY markdown polish (slice **04**)  
5. One board/ISSUE frontmatter note (slice **01**, single file)

## Forbidden

- `hands/gate`, auth, pairing, JWT  
- `scripts/devloop.py` monolith / **117–118** core extract  
- Velocity **131**, money-maker full stack (**PR 02**), sensory/CEO (**PR 03**)  
- Cross-lane edits; inventing features outside SCOPE  

## Team fit

| Seat | Does |
|------|------|
| `cursor` / strong model | Brain, factory, money-maker, security |
| `minimax` | Large vertical plugin slices |
| `minimax2` | Mini queue (Blackbox) |
| **`ministral`** | Same mini tier — docs + micro patches |

Parallel rules: [PARALLEL.md](PARALLEL.md).
