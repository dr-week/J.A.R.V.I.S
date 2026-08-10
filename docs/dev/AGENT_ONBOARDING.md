# Agent onboarding — names, manager, issues

When a **new AI coder** joins, do not invent ad-hoc names. Use the **registry + onboard script**.

Related: [MINIMAX.md](MINIMAX.md) · [PARALLEL.md](PARALLEL.md) · [agents.json](../board/agents.json)

---

## Is the old workflow enough?

| Before | Gap |
|--------|-----|
| Manual `--owner` ids | Collisions, no roster |
| `who` / NOW | Good for visibility, not onboarding |
| `brief` / LIVE_PLAN | Good work orders, not naming |

**Improved:** `devloop onboard` assigns the next id, registers the agent, suggests a **tier-appropriate** issue, prints paste-ready instructions (including **no plan re-approval**).

---

## Manager workflow (human or Cursor)

```bash
python scripts/devloop.py who
python scripts/devloop.py agents
```

**New Blackbox mini coder:**

```bash
python scripts/devloop.py onboard --tier mini --platform blackbox --display-name "MiniMax Coder 3"
```

**New standard slice coder (Blackbox main-style):**

```bash
python scripts/devloop.py onboard --tier standard --platform blackbox --display-name "MiniMax Main B"
```

Output includes:

- **`owner id`** (`minimax3`, `coder-004`, …)
- **Suggested issue** (mini → `starter` label / queue **115**, **116**, **122**)
- **`claim` + `brief` commands**

---

## New coder workflow (the AI)

1. Human runs `onboard` and pastes the owner block into the AI project.
2. AI runs `sync` → `claim` → `brief` with **its** `--owner` (never another agent's id).
3. AI implements acceptance — **no** “approve my plan?” ([EXECUTE.md](../../.blackbox/EXECUTE.md)).
4. `done` + `say` + `sync`.

---

## Tiers

| Tier | Typical issues | Owner id examples |
|------|----------------|-------------------|
| **mini** | `starter` label, ISSUE-115/116/122 | `minimax2`, `minimax3` |
| **standard** | Bridges, sync, plugins (022, 040…) | `minimax`, `coder-001` |
| **lead** | Human assigns; integration / review | `cursor`, `antigravity` |

Mark small issues with label **`starter`** in issue frontmatter.

---

## Registry file

[`docs/board/agents.json`](../board/agents.json) — append-only via `register` / `onboard`.

Manual register:

```bash
python scripts/devloop.py register --id minimax3 --tier mini --platform blackbox --display-name "Mini 3"
```

---

## Limits (unchanged)

- **2 parallel NOW slots** — onboard may say “wait” if full.
- Onboard **suggests**; human can override issue id on `claim`.
- Registry does not replace git — issues still live in `docs/board/issues/`.

---

## Quick reference

| Command | Role |
|---------|------|
| `devloop onboard` | Name + tier + suggest issue |
| `devloop agents` | Roster + who is on what |
| `devloop who` | NOW slots only |
| `devloop register` | Add id without full onboarding packet |
