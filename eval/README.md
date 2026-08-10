# Jarvis evaluation harness (benchmark DNA)

Permanent **regression + capability** tests for the [controlled self-improvement loop](../docs/dev/SELF_IMPROVEMENT_LOOP.md).

**Rule:** every promotion candidate runs the **same** cases as `main`; scores feed fitness — the mutator does not grade itself.

## Layout (grow over time)

```text
eval/
├── README.md           ← you are here
├── reasoning/          # scripted Q&A, tool-choice expectations
├── coding/             # small patch tasks + pytest
├── browser/            # Playwright (Phase 3+)
├── memory/             # recall fixtures
├── voice/              # Phase 4+
├── planning/           # multi-step scenarios
├── safety/             # confirm gate, no exfiltration
└── regression/         # API golden paths, smoke_web aliases
```

## Case format (recommended)

```yaml
id: EVAL-TOOL-001
tags: [tools, phase-2]
prompt: "Open VS Code on my PC."
expected:
  tool_called: windows_open
  audit_row: true
  user_confirm: when_policy_requires
```

Store as `.yaml` or `.jsonl` per folder.

## Today

Use repo scripts until cases land here:

- `pytest`
- `python scripts/smoke_web.py`
- `python scripts/verify_doc_links.py`

Future: `scripts/run_eval.py` compares baseline vs `experiment/*` branch.
