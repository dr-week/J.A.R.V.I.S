"""Code Runner Plugin (Phase 3 — Dev & AutoCoder Tools).

Allows Jarvis to run automated tests and execute isolated Python code snippets locally
for verification and autonomous debugging.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from backend.app.hands import registry


async def _dev_run_tests(test_path: str = "backend/tests") -> dict[str, Any]:
    """Run pytest on the given test path asynchronously and return test metrics."""
    clean_path = (test_path or "backend/tests").strip()
    cmd = [sys.executable, "-m", "pytest", clean_path]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60.0)

        out_text = stdout.decode("utf-8", errors="replace")
        err_text = stderr.decode("utf-8", errors="replace")
        passed = proc.returncode == 0

        # Truncate output to prevent token blowout
        summary = out_text[-2000:] if len(out_text) > 2000 else out_text

        return {
            "ok": passed,
            "exit_code": proc.returncode,
            "test_path": clean_path,
            "summary": summary,
            "stderr": err_text[:500] if err_text else "",
        }
    except asyncio.TimeoutError:
        return {"ok": False, "error": f"Pytest timed out after 60 seconds on {clean_path}"}
    except Exception as exc:
        return {"ok": False, "error": f"Failed to run tests: {exc}"}


async def _dev_eval_python(code: str) -> dict[str, Any]:
    """Execute a Python snippet in a subprocess and return stdout/stderr."""
    clean_code = (code or "").strip()
    if not clean_code:
        return {"ok": False, "error": "code parameter cannot be empty"}

    cmd = [sys.executable, "-c", clean_code]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15.0)

        out_text = stdout.decode("utf-8", errors="replace")
        err_text = stderr.decode("utf-8", errors="replace")
        passed = proc.returncode == 0

        return {
            "ok": passed,
            "exit_code": proc.returncode,
            "stdout": out_text[:2000],
            "stderr": err_text[:1000],
        }
    except asyncio.TimeoutError:
        return {"ok": False, "error": "Python execution timed out after 15 seconds"}
    except Exception as exc:
        return {"ok": False, "error": f"Failed to execute Python snippet: {exc}"}


registry.register(
    {
        "name": "dev_run_tests",
        "description": (
            "Run backend pytest suite or a specific test file. "
            "Returns pass/fail status, exit code, and output summary."
        ),
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "Path to test file or directory (default: 'backend/tests')",
                }
            },
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "exit_code": {"type": "integer"},
                "summary": {"type": "string"},
            },
        },
        "scopes": ["dev:read"],
        "tags": ["dev", "testing", "autocoder"],
    },
    _dev_run_tests,
)

registry.register(
    {
        "name": "dev_eval_python",
        "description": (
            "Execute a Python code snippet locally in a subprocess. "
            "Returns stdout, stderr, and execution status."
        ),
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python snippet to execute (e.g. 'import math; print(math.sqrt(16))')",
                }
            },
            "required": ["code"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
            },
        },
        "scopes": ["dev:write"],
        "tags": ["dev", "python", "autocoder"],
    },
    _dev_eval_python,
)
