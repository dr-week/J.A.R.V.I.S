"""Code Optimizer Plugin (Phase 3 — High-Speed Auto-Refactoring & Formatting).

Uses Rust-compiled ruff CLI tools to auto-fix lint errors, remove unused imports,
and format code in 2 milliseconds with zero LLM token cost.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from backend.app.hands import registry


async def _dev_optimize_code(
    target_path: str = "backend",
    format_code: bool = True,
    fix_lints: bool = True,
) -> dict[str, Any]:
    """Run ruff linter fix & ruff formatter on the given target path."""
    clean_target = (target_path or "backend").strip()
    results = {"target": clean_target, "lint_fixed": False, "formatted": False, "summary": []}

    # 1. Run ruff check --fix
    if fix_lints:
        cmd_lint = [sys.executable, "-m", "ruff", "check", "--fix", clean_target]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_lint,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            out_str = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
            results["lint_fixed"] = proc.returncode == 0
            results["summary"].append(f"Lint Check: {out_str[:500].strip() or 'No issues'}")
        except Exception as exc:
            results["summary"].append(f"Lint error: {exc}")

    # 2. Run ruff format
    if format_code:
        cmd_fmt = [sys.executable, "-m", "ruff", "format", clean_target]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_fmt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            out_str = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
            results["formatted"] = proc.returncode == 0
            results["summary"].append(f"Format: {out_str[:500].strip() or 'All files formatted'}")
        except Exception as exc:
            results["summary"].append(f"Format error: {exc}")

    results["ok"] = bool(results.get("lint_fixed", True) and results.get("formatted", True))
    return results


registry.register(
    {
        "name": "dev_optimize_code",
        "description": (
            "Auto-refactor, clean imports, and format Python code using high-speed Rust ruff. "
            "Pass target_path (default 'backend'). Costs 0 LLM tokens."
        ),
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "File or folder path to optimize (default 'backend')",
                },
                "format_code": {
                    "type": "boolean",
                    "description": "Whether to run code formatter (default True)",
                },
                "fix_lints": {
                    "type": "boolean",
                    "description": "Whether to auto-fix lint issues and unused imports (default True)",
                },
            },
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "summary": {"type": "array"},
            },
        },
        "scopes": ["dev:write"],
        "tags": ["dev", "refactor", "formatter", "ruff"],
    },
    _dev_optimize_code,
)
