# Scope

## In scope (product)

- Personal assistant with Soul + Mind + Hands + Presence
- Central brain with multi-device sync
- Phone (Android) + Windows + Web clients
- Expandable tool plugins (life domains + third-party)
- Docs + `devloop` so AI agents can build the product

## Explicitly out of scope (now)

- Replacing the entire OS
- Guaranteed UI automation inside every arbitrary app on day one
- Unrestricted shell / root without confirmation
- Training a custom foundation model from scratch
- Crypto protocol / blockchain sync (the “crypto” metaphor = portable synced identity, not a chain)
- Shipping always-on room mics without opt-in

## In scope vs examples

User examples (edit tasks, subtasks, reminders, contacts, plan today, search in app X) are **acceptance samples for Hands**, not a todo-app product definition.

| Example ask | What it proves |
|-------------|----------------|
| Edit a previous task / subtask | Durable state + update tools |
| List changes | Changelog / audit |
| Set reminder | Time-based execution |
| Edit specific contact | Precise device write |
| Plan today | Multi-source planning |
| Search in this app | Deep-link / intent execution |
| Non-Google integrate | Tool registry beyond one vendor |

## Phase boundaries

Work must stay inside the active phase unless an issue explicitly spans phases. See [ROADMAP.md](ROADMAP.md).

## Later (not never)

- Watch / car clients
- CRDT sync
- Full accessibility-driven UI automation
- Local LLM default
- Multi-user household profiles
- **Venture operator pack** — scout/analyst/growth plugins + metrics loop ([BUSINESS_OPERATOR.md](BUSINESS_OPERATOR.md)); human CEO on money/legal
- **Controlled self-improvement** — `experiment/*` + `eval/` + fitness; not hot-patching production ([dev/SELF_IMPROVEMENT_LOOP.md](dev/SELF_IMPROVEMENT_LOOP.md))
