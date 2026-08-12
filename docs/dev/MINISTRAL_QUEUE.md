# Ministral safe queue

**Boot:** [MINISTRAL.md](MINISTRAL.md) · **PR hub:** [PR_SPLIT.md](PR_SPLIT.md)

Only claim with `--owner ministral --tier mini`. One issue at a time. Re-check status before claim (`devloop sync`).

## Preferred now

| ID | Why mini-safe | Lane hint |
|----|---------------|-----------|
| [ISSUE-106](../board/issues/ISSUE-106.md) | P3 PWA / docs + small web | `clients/web/**`, PRESENCE_STACKS |
| Doc-only from [01-board-sync](pr-slices/01-board-sync.md) | Single ISSUE note file | `docs/board/issues/` one file |
| Doc-only from [04-ai-company-docs](pr-slices/04-ai-company-docs.md) | One MD polish | `AI-COMPANY/*.md` one file |

## Skip (not for Ministral)

| ID | Reason |
|----|--------|
| **115–116**, **122**, **124** | Config/types/tests — better stronger mini or Cursor |
| **117–118** | Devloop split |
| **130–131** | Velocity |
| **133** | Blocked on **128**; plugin template |
| **120** | Workflow may already be largely done — verify with Cursor first |

## After each done

```bash
python scripts/devloop.py sync --owner ministral
python scripts/devloop.py say --from ministral --to cursor --kind note -- "done ISSUE-XXX"
```
