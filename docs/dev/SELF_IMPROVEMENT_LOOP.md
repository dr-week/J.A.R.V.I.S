# Controlled self-improvement loop (FRIDAY-style)

**Codename:** FRIDAY = *inspect → propose → variant → test → compare → promote or revert*.

**Jarvis rule:** the mutator **never** judges itself. An **independent evaluator** (pytest, smoke, benchmark harness, human merge) decides keep vs reject. This extends [FUTURE.md](../FUTURE.md) adaptive mutation: habits and proposals are always in scope; **code** changes only via git branches and policy below.

Related: [LEARNING.md](../LEARNING.md) (user-facing habits) · [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) (task packets) · [AGENTS.md](../../AGENTS.md) · [SELF_STATE.md](SELF_STATE.md) · [ROADMAP.md](../ROADMAP.md) Phase 6–7.

---

## 1. Core architecture

```text
                    ┌──────────────┐
                    │    JARVIS    │
                    │   CURRENT    │
                    │  (main/ship) │
                    └──────┬───────┘
                           │
                           ▼
                    SELF-ANALYSIS
              (logs, SELF_STATE, board)
                           │
                           ▼
                 "What can be improved?"
                           │
                           ▼
                    MUTATION ENGINE
                    (scoped mutators)
                           │
                    creates Variant
                           │
                           ▼
                ┌─────────────────────┐
                │  experiment/* branch │
                │  + local sandbox     │
                └──────────┬──────────┘
                           │
                           ▼
                    AUTOMATED TESTS
                           │
                           ▼
                  BENCHMARK / EVAL
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              BETTER               WORSE
                 │                   │
                 ▼                   ▼
           PR + YOU MERGE        DELETE BRANCH
                 │
                 └──────────────→ LOOP
```

**Never mutate production in place.** Snapshot → experiment branch → sandbox → test → benchmark → promote / reject.

---

## 2. Jarvis DNA (what may change vs what is identity)

Mutable **modules**; not one blob rewrite.

| DNA strand | Repo anchor (examples) | Notes |
|------------|--------------------------|--------|
| Core reasoning | `backend/app/mind/` | Workflow graphs, planners |
| Personality | [PERSONA.md](../PERSONA.md), Soul config | Prompt + policy |
| Memory | Soul APIs, sqlite, vec | Retrieval params mutable L2 |
| Tool system | `tools/`, `hands/registry.py` | Router = common bottleneck |
| Safety rules | confirm gate, auth, audit | **Locked** (see §14) |
| Permissions | device bridge, WS auth | **Locked** without human |
| UI | `clients/web/`, Flutter Field, Flet | Separate eval buckets |
| Voice / vision | Phase 4+ plugins | Later eval suites |
| Coding ability | agents + `devloop` | Meta: repo improves repo |
| Performance targets | fitness weights in config | Human-set defaults |

Per module track: **version**, **dependencies**, **interfaces**, **tests**, **performance**, **known problems** (see [SELF_STATE.md](SELF_STATE.md)).

---

## 3. Mutation levels

| Level | What changes | Risk | Jarvis phase |
|-------|----------------|------|--------------|
| **L1 Prompt** | System prompts, persona snippets | Low | Now (Soul) |
| **L2 Config** | model, temperature, RAG k, timeouts | Low–med | `PATCH /config` + eval |
| **L3 Workflow** | Planner → tool → verifier graphs | Med | Mind loop ADRs |
| **L4 Code** | Python/TS in scoped paths | Med–high | `experiment/*` + CI |

Examples:

- **L1:** prompt V2 beats V1 on 100 scripted cases → store in Soul after eval.
- **L3:** add verifier step; benchmark task success 78% → 91% → promote workflow config.
- **L4:** `tool_router` patch on branch; `pytest` + `smoke_web.py` + tool-selection eval.

---

## 4. Code mutation path (fits this repo)

```text
Logs / eval failure cluster
        ↓
ISSUE-XXX or IMPROVE-YYY task packet
        ↓
Coding agent (cursor / minimax) — lane from PARALLEL.md
        ↓
git checkout -b experiment/tool-router-v4
        ↓
pytest · smoke_web · verify_doc_links · devloop verify ISSUE-XXX
        ↓
Evaluator compares fitness vs baseline on main
        ↓
PR → human merge OR branch delete
```

Git layout:

```text
main
 ├── experiment/memory-v2
 ├── experiment/planner-v3
 └── experiment/tool-router-v4
```

---

## 5. Evaluation system (`eval/`)

Without eval, mutations are blind. Permanent benchmark tree (grow incrementally; [eval/README.md](../../eval/README.md)):

```text
eval/
├── reasoning/
├── coding/
├── browser/          # later: Playwright
├── memory/
├── voice/
├── planning/
├── safety/           # confirm gate, no credential leak
└── regression/       # smoke_web + API golden paths
```

Each case: **id**, **prompt or action**, **expected outcome**, **tags** (phase, device).

Every candidate version runs the **same** suite; results stored as JSON for fitness (Phase 6+).

**Today (minimum):** `pytest`, `python scripts/smoke_web.py`, `python scripts/verify_doc_links.py`, `devloop verify ISSUE-XXX`.

---

## 6. Fitness function

Treat versions like organisms. Weights are **configurable**; example:

```text
FITNESS =
    30% task success (eval/)
  + 20% reliability (no false success, audit present)
  + 15% latency (p95 turn / tool)
  + 15% memory accuracy (recall@k on fixture set)
  + 10% coding (patch tasks in eval/coding/)
  + 10% resource (CPU/RAM budget)
```

```text
baseline (main)     fitness = 82.4
candidate branch    fitness = 86.7  → eligible for promote
candidate branch    fitness = 79.2  → reject
```

Venture SKUs may use **revenue-weighted** fitness ([ROADMAP.md](../ROADMAP.md) Phase 8) — separate from **product** fitness above.

---

## 7. Evolutionary batch (optional)

Instead of one mutation per cycle:

```text
              V20
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
      A        B        C
     81%      87%      84%
               │
               ▼
         promote B → V21
```

Run variants in **isolated worktrees** or CI matrix; cap parallel experiments (mutation budget).

---

## 8. Specialized mutators

| Mutator | Allowed paths | Forbidden |
|---------|---------------|-----------|
| Performance | hot paths, caches | security/, auth |
| Memory | retrieval, indexing | audit schema |
| Reasoning | prompts, planner | locked policies |
| Tool | router, registry | credential tools |
| UI | one client surface | other clients without eval |
| Prompt | persona templates | PERSONA trust ladder |
| Code refactor | scoped module | cross-cutting without ADR |
| Architecture | — | **Supervised only** (§14) |

---

## 9. Self-model — [SELF_STATE.md](SELF_STATE.md)

Living doc (human + agent edited): version, strengths/weaknesses from last eval, active experiment, goal. Drives **what to improve next** without the model guessing from vibes.

---

## 10. Self-generated development tasks

Weakness detected (logs or eval):

```text
Browser task failure rate = 19%
```

→ task packet (same schema as [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) Layer 7):

```yaml
id: IMPROVE-084
objective: Improve browser action verification
edit_paths:
  - clients/web/...   # example
do_not_edit:
  - backend/app/security/
  - memory/
success:
  - eval/browser/* pass rate >= 92%
tests:
  - pytest eval/browser
owner: cursor
```

Product improvements → `docs/board/issues/`; meta-improvements may use `docs/improve/` when we add that board.

---

## 11. Full loop (runtime + factory)

```text
             REAL WORLD / USER
                 │
                 ▼
              JARVIS
                 │
                 ▼
         LOGS + interaction_log
                 │
                 ▼
         PERFORMANCE + eval scores
                 │
                 ▼
          UPDATE SELF_STATE
                 │
                 ▼
        GENERATE TASK PACKET
                 │
                 ▼
          CODING AGENT + devloop
                 │
                 ▼
           experiment branch
                 │
          ┌──────┴──────┐
          ▼             ▼
        TEST          BENCHMARK
          └──────┬──────┘
                 ▼
            EVALUATOR (not mutator)
                 │
        ┌────────┴────────┐
        ▼                 ▼
      PROMOTE            REVERT
        │
        └──────────────→ LOOP
```

**Factory meta-loop:** building Jarvis via `devloop` *is* L4 mutation with you as evaluator on every merge.

---

## 12. Mutation budget (per cycle)

| Limit | Example cap |
|-------|-------------|
| Files changed | 10 |
| Lines changed | 500 |
| New dependencies | 2 (supervised if heavy) |
| Runtime regression | &lt; 10% |
| Memory regression | &lt; 15% |

**Required to promote:**

- tests pass
- safety eval pass
- fitness ≥ baseline (or explicit human waiver in issue notes)
- rollback = revert merge or delete branch

---

## 13. Three autonomy tiers

### Green — autonomous (after eval green)

- Prompts (L1), retrieval params (L2)
- Non-critical optimizations
- Test fixture additions

### Yellow — supervised (you approve)

- Architecture / new dependencies
- OS integrations, network permissions
- Major model swaps
- Cross-client behavior changes

### Red — locked (never self-modify)

- Security boundaries, credential storage
- Financial permissions, bulk comms
- Human approval mechanisms
- Audit log integrity, recovery/bootstrap

Matches [PERSONA.md](../PERSONA.md) confirm policy and [SCOPE.md](../SCOPE.md) (no unrestricted shell).

---

## 14. Critical principle

> **Jarvis must not decide it is better. The evaluator decides.**

Separate roles:

| Role | May |
|------|-----|
| **Mutator** (Mind / coding agent) | Propose diffs, branches, prompts |
| **Evaluator** (CI, scripts, benchmarks, you) | Score, merge, kill |

---

## 15. Rollout map

| When | Capability |
|------|------------|
| **Now** | devloop task packets; pytest/smoke as eval v0; SELF_STATE manual |
| **Phase 3–4** | L1–L2 automated A/B in Soul; interaction_log → weakness hints |
| **Phase 6 SDK** | Plugin DNA per tool; eval per plugin |
| **Phase 7** | Synapse-style local tuning **only** with frozen eval + human gate |
| **Phase 8** | Revenue fitness for venture SKUs only — not product safety |

Do **not** block Phase 2 exit on this doc; use it when opening **improvement** issues after Hands are trustworthy.

---

## Commands (evaluator v0)

```bash
python scripts/smoke_web.py
python scripts/verify_doc_links.py
pytest
python scripts/devloop.py verify ISSUE-XXX
```

When `eval/` grows:

```bash
python scripts/run_eval.py --baseline main --candidate experiment/tool-router-v4
```

(script TBD — track under improvement issue when pytest coverage lands, e.g. ISSUE-115).
