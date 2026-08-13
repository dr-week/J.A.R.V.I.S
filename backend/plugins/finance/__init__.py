"""Finances plugin — beancount plain-text accounting wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from backend.app.hands import registry

try:
    import beancount
    _HAS_BEANCOUNT = True
except ImportError:
    _HAS_BEANCOUNT = False

_LEDGER_FILE = Path(os.environ.get("JARVIS_LEDGER_FILE", "main.beancount"))


def _finance_add_transaction(date: str, payee: str, narration: str, amount: float, currency: str = "USD", account: str = "Expenses:Other") -> dict[str, Any]:
    """Add a plain-text accounting transaction entry."""
    entry = f"\n{date} * \"{payee}\" \"{narration}\"\n  {account}  {amount:.2f} {currency}\n  Assets:Cash\n"
    try:
        with open(_LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return {"status": "recorded", "payee": payee, "amount": amount, "currency": currency}
    except Exception as exc:
        return {"error": str(exc)}


def _finance_summary() -> dict[str, Any]:
    """Read summary of recorded financial ledger entries."""
    if not _LEDGER_FILE.exists():
        return {"count": 0, "message": "No ledger entries yet."}
    try:
        content = _LEDGER_FILE.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return {"entry_count": len(lines) // 4, "raw_snippet": content[-500:]}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "finance_add_transaction",
        "description": "Record a financial expense/transaction into plain-text ledger.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "payee": {"type": "string"},
                "narration": {"type": "string"},
                "amount": {"type": "number"},
                "currency": {"type": "string"},
                "account": {"type": "string"},
            },
            "required": ["date", "payee", "amount"],
        },
        "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
        "scopes": ["finance:write"],
        "tags": ["finance", "ledger", "accounting"],
    },
    _finance_add_transaction,
)

registry.register(
    {
        "name": "finance_summary",
        "description": "Get summary of plain-text financial ledger.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"entry_count": {"type": "integer"}}},
        "scopes": ["finance:read"],
        "tags": ["finance", "ledger", "accounting"],
    },
    _finance_summary,
)
