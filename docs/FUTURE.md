# Future — bigger plan (you, Jarvis, and the build crew)

This doc is the **north star** beyond the next issue. Roadmap phases stay the execution spine; this is **why** and **where we’re going**.

Related: [VISION.md](VISION.md) · [ROADMAP.md](ROADMAP.md) · [STRATEGY.md](STRATEGY.md) · [PARTNERSHIP.md](PARTNERSHIP.md) · [LEARNING.md](LEARNING.md) · [REQUIREMENTS.md](REQUIREMENTS.md) · [DOCS_MAP.md](DOCS_MAP.md)

---

## One picture

```text
                    ┌─────────────────────────────────────┐
                    │  YOU — goals, taste, veto, dreams   │
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │ Jarvis       │        │ Your robots  │        │ Build crew   │
  │ (runtime)    │        │ (plugins +   │        │ Cursor,      │
  │ Soul·Mind·   │◄──────►│  routines)   │        │ MiniMax,     │
  │ Hands        │        │              │        │ Antigravity, │
  └──────────────┘        └──────────────┘        │ you + board  │
         │                         │              └──────────────┘
         │    learns & suggests      │                      │
         └───────────────────────────┴──────────────────────┘
                         same git brain, same specs
```

- **Jarvis (product)** — the operator that lives with you: remembers, executes, adapts, suggests.
- **Your robots** — named automations you own (work plan, tidy room, home maintenance, daily admin). Not separate apps; **tools + triggers + audit** under one mind.
- **Us (build)** — docs, `devloop`, parallel agents shipping vertical slices while you steer persona, priorities, and acceptance.

**Co-labor covenant (earn, work, mutual future):** [PARTNERSHIP.md](PARTNERSHIP.md).

---

## Level ladder — earn more, do more, build tools (Iron Man arc)

Each **phase cleared** unlocks the next **operator tier**. Not cosmetics: new **Hands**, new **robots**, more **time and money leverage**. You are the pilot; Jarvis is the suit getting upgrades.

```text
  LEVEL   PHASE        YOU FEEL                         NEW POWER
  ─────   ─────        ────────                         ─────────
  L0      D0–D1        "We have a factory"              Board, agents, devloop
  L1      0 Skeleton   "It's alive"                     Chat on phone + PC, one brain
  L2      1 Soul       "It knows me"                    Memory, persona, habits forming
  L3      2 Hands      "It acts"          ◄── you are here (bridges ✅; Field UI ✅; **104** backend ✅; **142** Field confirm next)
  L4      3 Life       "It runs my domains"             Tasks, plan, connectors — YOUR tools
  L5      4 Voice      "It's always there"              Speak; tray; less friction
  L6      5 House      "The building is the suit"       Rooms, HA, scenes, ambient
  L7      6 SDK        "I forge new tools"              Plugins without rewriting core
```

| Level up | You **earn** (leverage) | We **build** (repo) | You **do more** |
|----------|-------------------------|---------------------|-----------------|
| **L1** | Less context-switch between devices | Brain + clients | Same mind everywhere you chat |
| **L2** | Less re-explaining yourself | Memory sync, learning | Jarvis recalls goals and prefs |
| **L3** | Less "open that for me" manual work | Device bridges, audit, confirm gate | PC + phone execute under policy |
| **L4** | Billable/admin hours back | Life plugins + semantic memory | Daily robots run work + home admin |
| **L5** | Hands-free blocks of time | STT/TTS, presence chrome | Operate while moving, driving, cooking |
| **L6** | Home ops without app hopping | Hub + IoT bridge | Voice in room → continues on phone |
| **L7** | Product/IP you can ship | Tool SDK, examples | New powers in days, not months |

**Iron Man intent (not cosplay):** trusted operator, executes under your authority — [VISION.md](VISION.md). **Suit upgrades** = phase exits on the board; **arc reactor** = local brain + plugin registry. **Workshop:** [dev/LAB_STACK.md](dev/LAB_STACK.md) · **Think ahead:** [dev/STARK_TIMELINE.md](dev/STARK_TIMELINE.md).

**Rule:** no skipping levels. Hands before house. Soul sync before pretending you're everywhere.

**Next level-up condition:** Phase 2 **exit** — close **101**, ship **104** (`confirm_request`), audited device action. Then Phase 3 = **tool forge** for life domains. Detail: [dev/STRATEGY_FORWARD.md](dev/STRATEGY_FORWARD.md).

---

## Product north star (for you)

**You wake up in a world that already knows your rhythm.**

- Mundane work **runs or is one confirmation away** — not “here are 10 steps.”
- **Future plans** live in Soul (goals, projects, seasons); Jarvis **re-plans** when life changes and **proposes** deltas — never rewrites your life silently.
- **The AI molds to you**: habits, tone, when to speak up, which robots to offer ([LEARNING.md](LEARNING.md), FR-S5–S8). Dismiss twice → it backs off. Accept → confidence grows.
- **Same personality** pocket → desk → room → car (later). Conversation **continues**, does not restart.
- **Trust ladder**: read/search auto; routines confirm-once; money/messages/delete always ask ([PERSONA.md](PERSONA.md)).

**End state (direction, not day-one):** a **personal fleet** of robots you defined or accepted, plus Jarvis inventing **new routine drafts** when it spots patterns — you approve, rename, or kill them.

---

## Build north star (for you + agents)

**The repo is a factory for Jarvis, not a one-off hack.**

| Principle | Meaning |
|-----------|---------|
| Spec before sprawl | SCOPE + board; agents claim issues, don’t wander |
| Two lanes max | Windows vs Android, plugin A vs B — ship in parallel |
| Vertical slices win | Bridge + protocol doc + `done` (see ISSUE-032) |
| You are PM + taste | Persona, which robots first, how pushy suggestions are |
| Agents are workers | `cursor`, `minimax`, `antigravity`, `claude` — interchangeable seats, same contract ([AGENTS.md](../AGENTS.md)) |

**Bigger build future:** more agents safely on the board; issues sized for one session; feedback bus so handoffs are automatic; eventually **Jarvis suggests its own backlog** from your goals (meta-issue: “user wants home maintenance robot” → draft issue for Phase 3).

---

## Horizons

### Horizon A — **Operator online** (now → next few milestones)

**Feel:** “It actually does things on my machines.”

| Deliver | Issue / phase |
|---------|----------------|
| Android bridge | ISSUE-033, Phase 2 |
| Memory + persona everywhere | ISSUE-022, Phase 1 |
| Pairing you trust | ISSUE-013 |
| Chat → tool → device → audit | 030–033 + Mind loop |

**Your robots (v0):** manual — you ask; Jarvis runs `windows_open` / `android_open` and logs it.

---

### Horizon B — **Life layer** (after Phase 2 exit)

**Feel:** “My week and my home admin run themselves with light touch.”

| Deliver | Phase |
|---------|-------|
| Tasks, subtasks, changelog, reminders | 3 (`040`, `041`) |
| Plan today / plan week from calendar + memory | 3 |
| First non-Google connector | `042` |
| Semantic memory (sqlite-vec) | 3 |
| Proactive suggestions (time + topic habits) | 1 + LEARNING rollout |
| Learned-memory push to all clients | sync polish |

**Your robots (v1):** named routines in config — e.g. `morning_brief`, `sunday_tidy`, `home_maintenance` — trigger: time, or “when I say”, or habit engine.

---

### Horizon C — **Ambient** (voice + presence)

**Feel:** “I don’t open an app; I speak and it’s already in context.”

| Deliver | Phase |
|---------|-------|
| STT/TTS on one client | 4 (`050`) |
| Tray / quick tile | `051` |
| Optional wake word | `052` |
| Shorter house replies, confirm only when needed | PERSONA voice rules |

**Your robots (v2):** voice-first; Jarvis **improvises** shorter paths (e.g. skip calendar read if you said “just remind me”).

---

### Horizon D — **House body**

**Feel:** “The house is part of the same conversation.”

| Deliver | Phase |
|---------|-------|
| Always-on hub | `060` |
| Home Assistant (or equivalent) | `061` |
| Room presence, continue thread | `062` |
| Scenes by voice | acceptance in Phase 5 |

**Your robots (v3):** tidy room = checklist + lights + vacuum + music; maintenance = HA sensors + reminders.

---

### Horizon E — **Forever expand**

**Feel:** “I add powers without forking the product.”

| Deliver | Phase |
|---------|-------|
| Tool SDK + template | `070`, `071` |
| Local LLM option | ADR-0007 follow-up |
| Third-party connectors at scale | 6 |

**Your robots (v4):** you publish plugins; Jarvis schedules them like built-ins; community patterns optional (still single-user first).

---

### Horizon F — **The Stark Endgame (Phase 7+)**

**Feel:** “It is an omnipresent, predictive entity with physical agency.”

| Deliver | Phase |
|---------|-------|
| Predictive Engine (Proactive Actions) | 7+ |
| Spatial AR Computing (WebXR / Unity) | 7+ |
| Continuous Local LLM LoRA Fine-Tuning | 7+ |
| Physical Actuation (ROS2 Integration) | 7+ |

**Your robots (v5):** Completely autonomous. Jarvis predicts you need to leave early due to traffic, adjusts the house temp, and physically sorts your desk via robotic actuators—all while you review the plan in AR glasses.

---

### Horizon G — **The Enterprise Protocol (Phase 8)**

**Feel:** “I am the Chairman of a fully autonomous, money-making business operating system.”

| Deliver | Phase |
|---------|-------|
| AI Corporate Hierarchy (CEO, Scout, Builder, Analytics) | 8 |
| Continuous Market Hunting (Reddit/App Store scraping) | 8 |
| Autonomous Portfolio Management (Micro-experiments) | 8 |
| Revenue as Feedback Loop (Stripe/Analytics webhooks) | 8 |

**Your robots (v6):** The system operates as a company. The Market Scout identifies a "boring money" gap. The AI CEO budgets $10 for it. Velocity builds the landing page. If conversion < 1%, the system automatically kills it and moves resources to the next experiment. You only intervene to approve high-risk scale-ups.

---

### Horizon H — **The Stark Masterplan (Phases 9, 10, 11)**

**Feel:** “I am Tony Stark. The AI builds physical reality, spans the globe, and operates at the speed of thought.”

| Deliver | Phase |
|---------|-------|
| The Forge Protocol (Parametric CAD & 3D Printing) | 9 |
| The EDITH Protocol (Global Telemetry & Swarm) | 10 |
| The Neural Link (BCI Zero-Latency Interface) | 11 |

**Your robots (v7):** You think about needing a custom mount. Jarvis reads the BCI intent (Phase 11), pulls satellite weather data to determine material stress (Phase 10), writes the OpenSCAD code, and streams the G-code to your 3D printer (Phase 9). The physical object is manufactured before you even speak a word.

---

## Adaptive “mutation” (what we mean)

| Yes | No |
|-----|-----|
| Habits, confidence, archived patterns | Runtime rewriting Python **on main** without review |
| Memories for goals and “future plan” | Pretending actions succeeded |
| Tone and brevity from fingerprinting | Sending messages/payments without policy |
| New routine **proposals** | Ignoring dismissals |
| `PATCH /config` persona name/tone | Hidden surveillance beyond documented logs |
| **Controlled** self-improvement: `experiment/*` branch + tests + evaluator | Mutator judges its own fitness |

Jarvis **co-evolves** with you through **data + suggestions + tools**, and may **improve its own repo** only via the git/eval loop — not uncontrolled in-process rewrites. Full design: [dev/SELF_IMPROVEMENT_LOOP.md](dev/SELF_IMPROVEMENT_LOOP.md) · living scores: [dev/SELF_STATE.md](dev/SELF_STATE.md).

---

## Example robot catalog (starter set — customize)

Use this as acceptance samples when we open Phase 3 issues. Rename freely.

| Robot | Trigger | Hands (examples) |
|-------|---------|------------------|
| **Work planner** | Weekday morning, or “plan my day” | Calendar read, task list, reminders, open focus app |
| **Future review** | Monthly or “where am I going” | Memory goals, draft milestones, set reminders |
| **Sunday tidy** | Learned Sunday PM | Checklist, timer, music, room scene (later) |
| **Home upkeep** | Monthly / HA signals | Maintenance list, order parts reminder, log done |
| **Shutdown** | Learned evening | Tomorrow preview, DND, lights scene (later) |
| **Inbox zero** | You invoke | Summarize, batch reminders, open mail client |

Jarvis should **merge/split** these as habits stabilize (e.g. tidy + shutdown → one “close the day” robot) — always visible to you in habits/memories APIs.

---

## Metrics that matter (not vanity)

| Metric | Why |
|--------|-----|
| Actions completed with audit row | Execute > explain |
| Suggestion accept vs dismiss rate | Learning quality |
| Time from intent → done on device | Hands health |
| Cross-device memory recall | Soul sync |
| Issues closed per week via devloop | Factory throughput |
| Your subjective “burden removed” | Ultimate PM test |

---

## Dependency spine (unchanged)

```text
D0 → D1 → 0 → 1 → 2 → 3
                 ↘ 4
            2/3/4 → 5 → 6
```

**Do not skip Phase 2 exit** for house fantasies; **do not skip Soul sync** for plugins — robots without one brain frustrate.

---

## Immediate “us” queue (actionable)

1. **MiniMax:** ISSUE-033 — Android bridge (mirror 032).
2. **Parallel:** ISSUE-022 — profile/memory on all devices.
3. **You:** Pick top 3 robots from the catalog; set suggestion aggressiveness (quiet / normal / pushy) when we add `LIFE_ROBOTS` config.
4. **Next wave:** 013 → 040/041 → proactive engine wired to suggestions in chat/push.

```bash
python scripts/devloop.py loop
python scripts/devloop.py status
```

---

## Closing

**Bigger:** house + fleet of personal robots + proactive mind that tracks your future.

**Better:** one brain, earned trust, open build loop so you and every agent add power without breaking the soul.

**For you and me:** you hold the vision and veto; Jarvis becomes the long-lived operator; we keep shipping proof on the board until the mundane is mostly **handled**.

When this doc and reality diverge, update [ROADMAP.md](ROADMAP.md) and log ADRs in [DECISIONS.md](DECISIONS.md).
