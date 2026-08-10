# Blackbox — execute mode (no plan re-approval)

Paste this at the top of **Main MiniMax** project instructions if Blackbox keeps asking to approve the same plan.

---

## Plan is already approved

The human **already approved** work by:

1. Putting the issue on the board with **acceptance criteria**
2. Telling you to run as owner **`minimax`**
3. **`devloop claim`** + **`devloop brief`** = your binding work order

**Do not** ask again:

- "Should I proceed with this plan?"
- "Do you approve this approach?"
- "Here's my plan, confirm before I start"

**Do** start implementation in the **same turn** after reading `docs/board/LIVE_BRIEF.md` and the issue file.

---

## When you MAY ask (only these)

| OK to ask | Not OK |
|-----------|--------|
| Acceptance is missing or contradictory | Re-stating the issue as a "plan" |
| You need a secret in `.env` you cannot invent | Choosing between two issues without `who` |
| `claim` fails (NOW full, owned by another) | Refactoring outside the issue |
| True fork: two valid designs **not** covered by ADR/issue | "Approve step 1 of 5" for work already on the board |

---

## Main MiniMax session (copy-paste)

```text
Owner: minimax. Execute mode ON.
Read docs/board/LIVE_BRIEF.md after: python scripts/devloop.py sync --owner minimax
If no NOW claim: python scripts/devloop.py claim ISSUE-022 --owner minimax (or issue human named).
Implement acceptance. No plan approval questions. Code first, then done + say to cursor.
```

---

## Main vs Coder 2

| Seat | Owner | Current typical work |
|------|-------|----------------------|
| **Main MiniMax** | `minimax` | Vertical slices: bridges, sync, backend+client |
| **Mini Coder 2** | `minimax2` | ISSUE-075, 076 — small backend/docs/scripts |

Check: `python scripts/devloop.py who`
