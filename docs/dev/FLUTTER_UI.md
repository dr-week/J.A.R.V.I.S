# Flutter UI — layout notes (Field Body)

**Product spec:** [FLUTTER_FIELD.md](FLUTTER_FIELD.md) — Flutter does **not** implement web chat.

Breakpoints below apply only if a thin confirmation/status UI needs responsive layout.

## Principles

1. **Portrait is the default** — thumb reach, one-handed chat, full-width bubbles.
2. **Landscape is adaptive, not a second app** — same routes; more horizontal space becomes a **rail** or **split**, not new navigation.
3. **Breakpoints** (Material 3–style, width in logical pixels):

| Token | Min width | Portrait phone | Landscape phone | Tablet / desktop |
|-------|-----------|----------------|-----------------|------------------|
| `compact` | 0 | Column: chat + composer | Column (tighter) | — |
| `medium` | 600 | — | Column + **leading rail** (icons) | Optional rail |
| `expanded` | 840 | — | **Split**: rail (240dp) + chat | Split + wider bubbles |

4. **Chat thread** always occupies the **main pane**; rail holds status dot, reconnect, new chat, bridge line (parity with `ui_gui.py`).
5. **Rotation** must not reset `session_id` or scroll position unless user taps **New chat**.
6. **Compact width** — follow [DESIGN.md](../DESIGN.md) responsive rule (`< 768px`): drawer or bottom nav; brand once; status zone never dropped.

## Wireframe (logical)

**Portrait**

```text
┌─────────────────┐
│ Jarvis    ⋮     │
├─────────────────┤
│                 │
│   messages      │
│                 │
├─────────────────┤
│ [ message… ] ➤  │
│ ● LLM · paired  │
└─────────────────┘
```

**Landscape / wide**

```text
┌────┬──────────────────────────┐
│ ●  │ Jarvis                   │
│ ⟳  ├──────────────────────────┤
│ 💬 │      messages            │
│    │                          │
│    ├──────────────────────────┤
│    │ [ message… ]          ➤  │
└────┴──────────────────────────┘
```

## MiniMax / agent lane

- Touch only `clients/flutter/**` for UI issues.
- Do not delete Flet until issue says deprecate.
- Verify: `flutter analyze` (when SDK present).

Related: [DESIGN.md](../DESIGN.md), [MINIMAX_UI.md](MINIMAX_UI.md) (Flet), [OSS.md](../OSS.md).
