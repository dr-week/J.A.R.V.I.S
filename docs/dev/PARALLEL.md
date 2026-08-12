# Parallel work — 2 people or 2 AIs

**Doc map:** [DOCS_MAP.md](../DOCS_MAP.md) · **Sync plan:** [SYNC_PLAN.md](SYNC_PLAN.md)

This project is designed for **two concurrent workers** (human+human, human+AI, or AI+AI).

**Primary pair in this repo:** Cursor (this side) + **Google Antigravity**, and sometimes **Claude Sonnet** instead of / in addition to Antigravity as the other coding agent.

## Rules

1. **Max 2 issues in NOW** — one claimed issue per worker
2. **Always set `--owner`** so the other worker does not steal your claim
3. **Do not edit files owned by the other issue** unless coordinated in Notes
4. **Pull / refresh board before claiming** so you see the other worker’s lock
5. Prefer **non-overlapping lanes** (see below)

## Who am I?

Pick a stable owner id and reuse it every session:

| Role | Example `--owner` | Notes |
|------|-------------------|--------|
| Cursor (this IDE) | `cursor` | Default for work started here |
| Google Antigravity | `antigravity` | Other AI on this project |
| Claude Sonnet | `claude` | When Sonnet is the other agent |
| Human A / B | `alice` / `bob` | People |
| Blackbox / MiniMax (optional) | `minimax` | Main Blackbox seat — large vertical slices / cross-file integration — see [MINIMAX.md](MINIMAX.md) |
| Blackbox MiniMax **second seat** | `minimax2` or `minimax-mini` | Parallel mini coder — helpers, docs, one-file UI slices — **unique** `--owner`, never reuse `minimax` |
| **Ministral** (small local/cloud) | `ministral` | Mini tier only — docs + micro patches — [MINISTRAL.md](MINISTRAL.md) · [MINISTRAL_QUEUE.md](MINISTRAL_QUEUE.md) |

**MiniMax rules:** [docs/dev/MINIMAX.md](MINIMAX.md) · Blackbox entry: [.blackbox/RULES.md](../../.blackbox/RULES.md)  
**Ministral rules:** [docs/dev/MINISTRAL.md](MINISTRAL.md) — always `next --owner ministral --tier mini`

## Commands (per worker)

```bash
# See both workers
python scripts/devloop.py status

# Cursor side
python scripts/devloop.py next --owner cursor
python scripts/devloop.py claim ISSUE-010 --owner cursor
python scripts/devloop.py prompt --owner cursor

# Google Antigravity side
python scripts/devloop.py next --owner antigravity
python scripts/devloop.py claim ISSUE-011 --owner antigravity
python scripts/devloop.py prompt --owner antigravity

# Claude Sonnet side (when that is the other AI)
python scripts/devloop.py next --owner claude
python scripts/devloop.py claim ISSUE-012 --owner claude
python scripts/devloop.py prompt --owner claude

# Progress / finish / free the slot
python scripts/devloop.py update ISSUE-011 --note "windows client stub compiling"
python scripts/devloop.py done ISSUE-011
python scripts/devloop.py release ISSUE-011 --owner antigravity
```

## Safe parallel lanes

| When | Worker A (`cursor`) | Worker B (`antigravity` or `claude`) |
|------|---------------------|--------------------------------------|
| Phase 0 (after health) | `ISSUE-011` Windows client | `ISSUE-012` Android client |
| Phase 1 vs early Hands | Soul memory (`021`) | Tool registry (`030`) — avoid same files |
| Phase 2 | Windows bridge `032` | Android bridge `033` |
| Phase 3 | Plugin tasks `040` | Plugin reminders `041` |
| **Presence (2026)** | **Web** `clients/web/**` (102 sessions) | **Flutter Field** `clients/flutter/**` (101) — **not** chat parity |
| **Presence** | **Backend** tools/API | **Windows** tray/voice `clients/windows/**` |
| Helpers / docs | `085` Repo Navigator | `086` Board Copilot |
| Docs vs code | Docs/ADR only | Implementation issue |

**Avoid:** two workers editing `scripts/devloop.py`, the same client, the same plugin, or the same helper file at once.

## Conflict policy

- `claim` on an issue owned by someone else → **rejected** (use `--steal` only if that worker is gone)
- Same owner may re-claim their issue
- If git conflicts: the issue owner resolves; other worker stays on their lane
- Shared docs (`ARCHITECTURE`, `ROADMAP`): one worker at a time, or A writes ADR while B codes

## Sync rhythm + feedback bus

1. Both: `devloop loop` (slots + next tips + recent handoffs)
2. Each: `devloop inbox --owner ME`
3. Each: `next --owner ME` → `claim` → `prompt --owner ME`
4. Message the other AI: `devloop say --from ME --to THEM --kind note -- "…"`
5. Optional branches: `worker/cursor-ISSUE-010`, `worker/antigravity-ISSUE-011`
6. Merge sequentially if both touch `backend/`; parallel merge OK if different top-level dirs

Claim/done **auto-post** to `docs/board/feedback.jsonl` → `FEEDBACK.md`.

Full protocol: [FEEDBACK_LOOP.md](FEEDBACK_LOOP.md)

See also [PROCESS.md](PROCESS.md) and [STRATEGY.md](../STRATEGY.md).
