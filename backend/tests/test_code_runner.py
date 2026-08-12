"""Tests for code_runner plugin."""
from __future__ import annotations

import pytest
from backend.plugins.code_runner import _dev_eval_python, _dev_run_tests
from backend.app.hands.registry import REGISTRY


@pytest.mark.asyncio
async def test_code_runner_tools_registered():
    """Verify tool registration in REGISTRY."""
    assert "dev_run_tests" in REGISTRY
    assert "dev_eval_python" in REGISTRY


@pytest.mark.asyncio
async def test_dev_eval_python_success():
    """Test evaluating a valid Python snippet."""
    res = await _dev_eval_python("print('hello autocoder')")
    assert res["ok"] is True
    assert res["exit_code"] == 0
    assert "hello autocoder" in res["stdout"]


@pytest.mark.asyncio
async def test_dev_eval_python_error():
    """Test evaluating code with an error."""
    res = await _dev_eval_python("raise ValueError('test error')")
    assert res["ok"] is False
    assert res["exit_code"] != 0
    assert "ValueError: test error" in res["stderr"]


@pytest.mark.asyncio
async def test_dev_run_tests_success():
    """Test running pytest on test_health.py."""
    res = await _dev_run_tests("backend/tests/test_health.py")
    assert res["ok"] is True
    assert res["exit_code"] == 0
    assert "passed" in res["summary"]
