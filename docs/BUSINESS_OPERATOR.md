# Business operator — profit loop (design)

**Not a promise of autonomous income.** A **repeatable loop** Jarvis can support when you choose to run a venture — under [PARTNERSHIP.md](PARTNERSHIP.md) rules (human confirm on money, legal, public claims).

Related: [REQUIREMENTS.md](REQUIREMENTS.md) FR-M2 · [FUTURE.md](FUTURE.md) · [TOOL_SCHEMA.md](TOOL_SCHEMA.md)

---

## Objective function (not “make money”)

Maximize **legitimate net profit** subject to:

| Constraint | Jarvis mechanism |
|------------|------------------|
| Minimum product quality | You define; Builder output reviewed before launch |
| Customer satisfaction | Support tools + memory of complaints |
| Legal/compliance | **Human confirm always** — payments, contracts, ads claims |
| Reputation / trust | [PERSONA.md](PERSONA.md), no dark patterns |

Store weekly objective + constraints in Soul (`work_priority_week`, `venture_constraints`).

---

## The loop (8 steps)

```text
MARKET → PROBLEM → VALIDATION → PRODUCT → LAUNCH → CUSTOMERS → REVENUE → DATA → OPTIMIZE → (repeat)
```

| Step | What happens | Jarvis today | Jarvis Phase 3+ |
|------|----------------|--------------|-----------------|
| 1 Find problem | Scout signals | You + chat research | `scout_*` tools (search, RSS, manual paste) |
| 2 Validate demand | Evidence of paying users | Memory + notes | Analyst scoring tool |
| 3 Choose opportunity | Scorecard | You decide | Structured `opportunity_brief` in DB |
| 4 Build | Code/content/product | **devloop agents** build Jarvis; you build SKUs | Builder plugins + coding agent |
| 5 Launch | Site/market/social | Hands: URLs, drafts | Growth content tools |
| 6 Measure | Funnel metrics | Manual / spreadsheet | Analytics plugin + Soul metrics |
| 7 Improve | Hypothesis → test | Issues + memory | CEO orchestration pass |
| 8 Repeat | Kill or double down | Board + `devloop` | Automated backlog proposals |

**Meta today:** this repo’s **devloop** loop (board → claim → ship → measure done → next) *is* a profit loop for building Jarvis the asset ([PARTNERSHIP.md](PARTNERSHIP.md) Layer 2–3).

---

## Five roles (multi-agent business)

| Role | Job | Evidence required | Maps to |
|------|-----|-------------------|---------|
| **Scout** | Find opportunities | Links, search volume, complaints | Future tools + Mind research |
| **Analyst** | Score proceed/kill | Demand, competition, margin, build time | Structured JSON scorecard; **you** approve |
| **Builder** | Ship MVP | Repo, deploy URL, acceptance tests | Cursor/MiniMax + **you** merge |
| **Growth** | Traffic & conversion | Analytics numbers, not vibes | Plugins; ads/spend = confirm always |
| **CEO** | Allocate attention | Actual revenue/cost data | **You** are CEO; Jarvis proposes next actions |

**CEO rule (human or Jarvis draft):** never promote Scout hype without Analyst numbers and Growth measurements.

Example message bus (future):

```text
SCOUT → opportunity_id + sources
ANALYST → { proceed: yes|no, est_margin, build_days, confidence }
BUILDER → { artifact_url, tests_passed }
GROWTH → { visitors, conversions, revenue, cac }
CEO → { decisions: [ ... ], requires_human: true }
```

Implement as **plugins + memory**, not five separate chatbots, unless ADR says otherwise.

---

## Tools matrix (capability → implementation)

| Capability | Tooling | Jarvis path |
|------------|---------|-------------|
| Market research | Web/search | Phase 3 `web_search` / manual; no scraping ToS violations |
| Coding | IDE + agents | **Already:** `devloop`, repo agents |
| Analytics | DB/dashboard | SQLite metrics table or export CSV |
| Product creation | Code/media gen | Hands + external APIs; confirm on publish |
| Marketing | Content gen | Draft posts; **you** post |
| Support | Support agent | Chat + memory; Phase 3 comms plugins |
| Experimentation | A/B | Feature flags plugin (future) |
| Financial tracking | Sheets/API | Plugin; **confirm always** on payments |
| Memory | PROJECT_STATE | Soul memories + `venture/*` keys |
| Planning | Orchestrator | Mind plan→act; weekly CEO review ritual |

No custom model training required — **model + tools + memory + loop**.

---

## Phased productization (honest)

| Phase | Business-operator feature |
|-------|----------------------------|
| **Now** | Partnership doc, devloop ship loop, audit log, confirm gate |
| **2 exit** | Reliable Hands — launch checklist execution |
| **3** | Life/admin plugins (tasks, calendar, files) — **Layer 1** time savings |
| **3–4** | Optional `venture` plugin pack: scout brief, scorecard, metrics ingest |
| **6** | SDK so **your** robots are sellable IP ([PARTNERSHIP.md](PARTNERSHIP.md) Layer 3) |

**Out of scope until issue + ADR:** autonomous ad spend, autonomous checkout, spam outreach, market manipulation.

---

## Weekly CEO ritual (you + Jarvis)

1. Pull metrics (even a spreadsheet) into chat or memory.
2. Ask: *What had highest $/hour? What failed validation?*
3. `devloop say` or Soul update → next week’s **one** venture bet + **one** build issue.
4. Agents execute only what’s on the board with acceptance.

---

## One sentence

Teach Jarvis a **measured profit loop with evidence gates** — not a vague “get rich” goal — and keep **you** as CEO on money and promises.

Ten layers and venture OS: sections below · **15 ways + 90-day plan:** [VENTURE_EARN_PLAN.md](VENTURE_EARN_PLAN.md).

---

## Ten layers — how far can you push? (with Jarvis gates)

Each layer is **possible in principle**; Jarvis implements them **incrementally**. High-risk layers need **human approve** and respect site ToS / law.

| # | Capability | What it does | Jarvis implementation | Gate |
|---|------------|--------------|------------------------|------|
| **1** | **Opportunity hunt** | Continuous scan → scored gaps | Scout tools: RSS, manual exports, search APIs; **not** blind scraping | ToS + rate limits; you approve sources |
| **2** | **Reverse-engineer winners** | Decompose product → differentiated play | Analyst tool: structured brief from URL/docs you supply | No trademark/copy infringement |
| **3** | **Micro-experiments** | Many landing pages / waitlists | Experiment registry in SQLite; kill rules | Spend cap per experiment (you set) |
| **4** | **Digital products** | SaaS, templates, APIs, etc. | Builder = agents + plugins; low marginal cost | You own deploy + merchant accounts |
| **5** | **Portfolio** | Many small SKUs, not one bet | `venture/portfolio` table: MRR, status, kill date | CEO review weekly |
| **6** | **AI “company”** | Departments + KPIs | One brain, role-tagged tools + budgets in memory | Finance/legal = human only |
| **7** | **Self-managed backlog** | CEO picks highest ROI task | **Today:** `devloop` + `LIVE_PLAN` + issues; **Venture:** second board or `venture/ISSUE-*.md` | Task packets → claimed issues |
| **8** | **Revenue feedback** | Optimize business, not just tests | Metrics ingest → rank features by Δconversion/MRR | Needs real analytics hook |
| **9** | **Auto-kill losers** | Budget + timebox → shutdown | Rules engine: if metrics below threshold → `status: killed` + archive | **You** confirm kill if $ or brand at stake |
| **10** | **Boring money** | B2B admin, compliance, files | Phase 3 plugins (invoice, ETL, schedulers) | Often best ROI — prioritize in Scout |

---

## Ultimate architecture (venture OS)

```text
                  ┌───────────────┐
                  │   AI CEO      │  ← drafts; YOU approve money/contracts/kill
                  └───────┬───────┘
                          ↓
                  ┌───────────────┐
                  │ MARKET SCOUT  │  ← layer 1–2 signals
                  └───────┬───────┘
                          ↓
                  ┌───────────────┐
                  │ OPPORTUNITY   │
                  │    SCORER     │  ← Analyst JSON scorecard
                  └───────┬───────┘
                          ↓
                  ┌───────────────┐
                  │ EXPERIMENT    │
                  │   MANAGER     │  ← layer 3, 9 (budget, kill)
                  └───────┬───────┘
                          ↓
             ┌────────────┴────────────┐
             ↓                         ↓
        ┌─────────┐               ┌─────────┐
        │ BUILDER │               │ GROWTH  │
        └────┬────┘               └────┬────┘
             ↓                         ↓
             └────────────┬────────────┘
                          ↓
                    REAL CUSTOMERS
                          ↓
                       REVENUE
                          ↓
                    ┌───────────┐
                    │ ANALYTICS │  ← layer 8
                    └─────┬─────┘
                          ↓
                    CEO learns → NEXT DECISION → devloop / venture board
```

**Jarvis mapping:** Scout/Analyst/Growth/Analytics = **Phase 3+ plugins**; Builder = **agents + Hands**; CEO = **Mind + you**; Experiment Manager = **devloop pattern** extended to ventures.

---

## Authority matrix (realistic autonomy)

| Action | AI alone | AI + low-risk auto | Human required |
|--------|----------|-------------------|----------------|
| Read public reviews you paste | ✅ | | |
| Scheduled RSS / API fetch (allowed ToS) | | ✅ | |
| Create landing page draft in repo | | ✅ | |
| Deploy to production | | | ✅ |
| Ad spend, payment links, contracts | | | ✅ always |
| Kill experiment (no sunk cost) | | ✅ if rules pre-agreed | ✅ if revenue/brand |
| Open new merchant / legal entity | | | ✅ |
| Email customers at scale | | | ✅ |

Pattern: **AI proposes → executes low-risk → you approve high-risk** ([PERSONA.md](PERSONA.md) confirm policy).

---

## Layer 7 — Orchestrator + task packet (fits devloop today)

**Jarvis repo (building the platform):**

```text
docs/board/LIVE_PLAN.md + PROJECT_STATE (you / Soul)
        ↓
AI lead (cursor) + devloop next/claim
        ↓
ISSUE-XXX = Task Packet (acceptance = definition of done)
        ↓
Coding agent implements
        ↓
pytest / smoke / verify_doc_links
        ↓
devloop done → FEEDBACK.md handoff
        ↓
LIVE_PLAN regenerated
```

**Future venture repo or `docs/venture/` board:**

Same loop with **ROI field** on each issue (`expected_margin`, `experiment_id`). CEO ranks by **expected business value**, not only P0/P1.

### Task packet (minimum schema)

```yaml
id: VENTURE-003
hypothesis: "B2B PDF batch converter"
experiment_budget_inr: 10000
timebox_days: 7
kill_if:
  signups_lt: 20
  conversion_lt: 0.01
expected_roi: medium
acceptance:
  - Landing page live
  - Analytics pixel firing
  - One paying customer OR kill decision recorded
owner: minimax2
```

Store under `docs/venture/experiments/` when you start — **do not** mix with Jarvis product Phase 2 issues until board exit.

---

## Layer 3 & 5 — Experiments and portfolio

**Micro-experiment types:** landing, waitlist, prototype, demo video, price test.

**Portfolio row:**

| Field | Example |
|-------|---------|
| `sku_id` | `pdf-batch-v1` |
| `mrr` | 800 |
| `status` | `live` / `killed` / `paused` |
| `cac` | 31 |
| `last_decision` | `scale_marketing_20pct` |

AI **recommends** shut down; pre-agreed rules can auto-`paused`; **you** confirm kill if material.

---

## Layer 8 — Optimize for revenue, not only “tests pass”

| Signal | Use |
|--------|-----|
| Conversion Δ | Rank features |
| MRR Δ | Portfolio allocation |
| Retention / churn | Kill or fix |
| Support tickets | Quality constraint |

Wire into Soul weekly: `venture_metrics_snapshot` (JSON). CEO prompt: *“Given these numbers, what is the highest EV task packet?”*

---

## Layer 10 — “Boring money” scout prompts

Prioritize Scout searches toward:

- Internal reporting, invoices, doc conversion, data cleaning
- Compliance workflows, scheduling, file pipelines
- Industry calculators, dashboards, SMB automation

Often **easier monetization** than consumer apps — align with Jarvis Hands (execute admin) not hype.

---

## Suggested build order (venture OS on Jarvis)

| Order | Deliverable | Depends on |
|-------|-------------|------------|
| 1 | Soul keys + weekly CEO ritual | now |
| 2 | `opportunity_brief.json` schema + Analyst plugin stub | Phase 3 |
| 3 | `docs/venture/experiments/` + kill rules doc | Phase 3 |
| 4 | Metrics ingest tool (CSV or Stripe read-only) | Phase 3 + human API keys |
| 5 | Scout feeds you **curate** (RSS, not illegal scrape) | Phase 3 |
| 6 | Portfolio dashboard (web or SQLite views) | Phase 3–4 |
| 7 | ROI-sorted venture devloop (separate board) | Phase 3 exit + ADR |

**Do not skip:** Phase 2 exit (confirm WS, audit, trust) — autonomous venture ops without trust rails is a liability.

---

## One paragraph (ultimate)

An **AI business OS** continuously searches (within rules), scores opportunities, runs bounded experiments, builds digital products cheaply, measures revenue, kills failures fast, scales winners in a **portfolio** — with **you** as final authority on money, law, and brand. Jarvis is the right chassis: **one brain, tools, memory, confirm gate, devloop backlog** — extended from “ship Jarvis” to “ship your SKUs” when you open the venture lane.

See also: [PARTNERSHIP.md](PARTNERSHIP.md) · [STARK_TIMELINE.md](dev/STARK_TIMELINE.md) (product vs venture timing).
