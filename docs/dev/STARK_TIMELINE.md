# Stark timeline — think ahead (strategy only)

**Not a commitment calendar** — a decision lens. Board truth stays [LIVE_PLAN.md](../board/LIVE_PLAN.md). Doctrine: [LAB_STACK.md](LAB_STACK.md) · levels: [FUTURE.md](../FUTURE.md).

---

## The arc (one paragraph)

Tony does not build the house AI before the suit can **see, log, and ask permission**. Jarvis is the same: **finish Hands (L3)** with one chat brain, audited tools, and real confirms — then **forge life robots (L4)** — then **voice and rooms (L5–L6)** — then **hand others the SDK (L7)**. Every season adds OSS only when the previous layer is **instrumented and boring**.

---

## Timeline (think ahead)

```text
        TODAY                          6 MO                         12–18 MO                    24+ MO
          │                              │                              │                          │
   ┌──────▼──────┐                ┌──────▼──────┐                ┌──────▼──────┐           ┌─────▼─────┐
   │ L3 Hands    │   exit when    │ L4 Life     │   voice when   │ L5 Voice    │           │ L6 House  │
   │ 101+104     │ ─────────────► │ plugins     │ ─────────────► │ ambient     │ ────────► │ HA rooms  │
   │ vitals/logs │   101+104+audit│ memory vec  │   L4 gate      │ PWA default │           │ MQTT      │
   └─────────────┘                └─────────────┘                └─────────────┘           └───────────┘
        │                              │                              │
   workshop:                    Friday runs:                   same mind:
   pytest, Settings,            tasks, calendar,              pocket→desk→room
   confirm WS                   your robots                   one thread
```

---

## What Stark would prioritize (ordered)

| # | Move | Why ahead of time |
|---|------|-------------------|
| 1 | **Close the reactor loop** — **104** confirm on WS, **107** token on `/ws` | Without trust rails, scaling presence = scaling risk |
| 2 | **Instrument before features** — **115–116**, **124**, **125** vitals | You cannot debug a suit you cannot read |
| 3 | **One HUD** — web chat; Field executes; strip Flutter chat (**103**) | Two JARVIS voices = user confusion and agent thrash |
| 4 | **PWA as desk default (**106**)** | Stark’s desk is a screen + voice, not a second Electron chat |
| 5 | **Phase 3 memory** — sqlite-vec + alembic (**123**) when schema grows | Semantic recall is L4; migrations before data debt |
| 6 | **Voice lab only until Phase 4 exit** — **126** prototype, Whisper/Piper prod later | Wake word before confirm gate is movie logic, not engineering |
| 7 | **House last** — HA scenes after voice path works | The building is a body, not the brain |
| 8 | **ADR before Iron Legion** — **127** Celery vs APScheduler | Queues are for proven load, not workshop daydreams |

---

## Two parallel “factories”

| Factory | Who | Output |
|---------|-----|--------|
| **Armor line** (product) | minimax + cursor + antigravity | Brain, bridges, web, Field, plugins |
| **Workshop line** (quality) | minimax2 | pytest, types, deps micro-slices, PWA, CI **120** |

Stark runs both: **never stop shipping slices** while **never skipping instrumentation**.

---

## Decision checkpoints (ask at each)

1. **Does this need a new UI surface?** If yes → probably no (web or Field only).
2. **Does this need a new process/daemon?** If yes → ADR + phase gate (**127** template).
3. **Can MiniMax do it in one lane / one PR?** If no → split like **119→115**.
4. **Does it work offline on your LAN?** Prefer yes for voice/house; cloud is optional enhancer.

---

## North star checks (yearly)

- Same **persona + memory** on phone, PC, and (later) room.
- **Execute > explain** on routine work; confirm on irreversible.
- **You own** models, data, and home fabric — Jarvis integrates OSS, does not rent your identity.

---

## Related

[STRATEGY_FORWARD.md](STRATEGY_FORWARD.md) · [ROADMAP.md](../ROADMAP.md) · [PARTNERSHIP.md](../PARTNERSHIP.md)
