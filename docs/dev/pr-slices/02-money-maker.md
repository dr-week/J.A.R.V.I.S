# Slice 02 — Money-maker plugin + skills

**Hub:** [../PR_SPLIT.md](../PR_SPLIT.md) · **Siblings:** [01](01-board-sync.md) · [03](03-sensory-ceo.md) · [04](04-ai-company-docs.md)

## Major

Add the venture/finance **tools + skills** stack as one product PR (not board, not brain sensory).

## Scope

- `tools/money_maker/**`
- `skills/__init__.py`, `skills/business_idea_generator.py`, `skills/market_scanner.py`, `skills/opportunity_scraper.py`
- `modules/**` (finance, math, strategy)
- `core/**` (`base_skill.py`, `risk_manager.py`)
- `jarvis_main.py`
- `scripts/market_scout.py`
- `requirements.txt`

## Optional attach

- `pyproject.toml` + `uv.lock` if `fastmcp` is required for this slice — otherwise leave in hold-outs ([hub](../PR_SPLIT.md#hold-out-not-in-0104)).

## Reviewer lane

Product / tools (`cursor` or venture owner).

## Suggested branch

`pr/money-maker`
