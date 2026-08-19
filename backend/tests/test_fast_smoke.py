"""Fast smoke tests — run with: pytest -m fast (target: <2s total).

Covers the three highest-risk surfaces for 4GB VRAM safety:
  1. Intent router classification (no wrong tool injection)
  2. Tool schema validity (all registered tools have correct schema shape)
  3. Context window pruning (MAX_CONTEXT_TURNS enforced)
  4. Output token budget guard (_sanitize_tool_output truncation)
  5. @tool decorator registration
"""
import json
import pytest


# ─── 1. Intent Router ────────────────────────────────────────────────────────

@pytest.mark.fast
def test_router_code_domain():
    from backend.app.mind.router import classify_intent_fast
    tools = classify_intent_fast("run python code")
    assert "velocity_build" in tools or "dev_eval_python" in tools


@pytest.mark.fast
def test_router_tier3_conversational_returns_empty():
    """Conversational prompt must return 0 tools — no VRAM wasted."""
    from backend.app.mind.router import classify_intent_fast
    tools = classify_intent_fast("how are you today")
    assert tools == []


@pytest.mark.fast
def test_router_workspace_edit_domain():
    from backend.app.mind.router import classify_intent_fast
    tools = classify_intent_fast("edit the main.py file")
    assert "file_edit_strict" in tools


# ─── 2. Tool Schema Validity ─────────────────────────────────────────────────

@pytest.mark.fast
def test_all_registered_tools_have_valid_schema():
    """Every registered tool must expose a valid parameters JSON schema."""
    from backend.app.hands.registry import REGISTRY
    for name, tool in REGISTRY.items():
        assert "parameters" in tool, f"Tool '{name}' missing parameters key"
        params = tool["parameters"]
        assert params.get("type") == "object", f"Tool '{name}' parameters.type must be 'object'"
        assert "properties" in params, f"Tool '{name}' parameters missing 'properties'"
        assert isinstance(params["properties"], dict), f"Tool '{name}' properties must be a dict"


@pytest.mark.fast
def test_all_registered_tools_have_risk_level():
    from backend.app.hands.registry import REGISTRY
    valid = {"auto", "confirm_once", "confirm_always"}
    for name, tool in REGISTRY.items():
        rl = tool.get("risk_level")
        assert rl in valid, f"Tool '{name}' has invalid risk_level: {rl}"



# ─── 3. Context Window Pruning ────────────────────────────────────────────────

@pytest.mark.fast
def test_context_window_prunes_to_max_turns():
    from backend.app.mind.message_builder import build_messages, MAX_CONTEXT_TURNS
    long_history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"message {i}"}
        for i in range(30)
    ]
    msgs = build_messages("sys", long_history, "new message")
    # system + MAX_CONTEXT_TURNS - 1 history + new user = MAX_CONTEXT_TURNS + 1
    assert len(msgs) <= MAX_CONTEXT_TURNS + 2


# ─── 4. Token Budget Guard ────────────────────────────────────────────────────

@pytest.mark.fast
def test_sanitize_passes_small_output():
    from backend.app.mind.openai_loop import _sanitize_tool_output
    result = {"ok": True, "result": "small output"}
    out = _sanitize_tool_output("test_tool", result)
    assert json.loads(out) == result  # Small output: parseable JSON unchanged


@pytest.mark.fast
def test_sanitize_truncates_giant_char_output():
    from backend.app.mind.openai_loop import _sanitize_tool_output, _TOOL_OUTPUT_MAX_CHARS
    big = {"result": "x" * 5000}
    out = _sanitize_tool_output("workspace_map_tree", big)
    assert len(out) <= _TOOL_OUTPUT_MAX_CHARS + 80  # +80 for the truncation notice
    assert "truncated" in out


@pytest.mark.fast
def test_sanitize_truncates_many_lines():
    from backend.app.mind.openai_loop import _sanitize_tool_output, _TOOL_OUTPUT_MAX_LINES
    many_lines = "\n".join([f"line {i}" for i in range(200)])
    result = {"result": many_lines}
    out = _sanitize_tool_output("dev_run_tests", result)
    assert out.count("\n") <= _TOOL_OUTPUT_MAX_LINES + 5
    assert "truncated" in out


# ─── 5. @tool Decorator ───────────────────────────────────────────────────────

@pytest.mark.fast
def test_tool_decorator_registers_and_infers_schema():
    """@tool must auto-register and generate correct JSON schema from type hints."""
    from backend.app.hands.registry import REGISTRY

    # Only import decorator (does not double-register if tool_name is unique)
    tool_name = "_test_decorator_smoke_tool_xyz"
    if tool_name not in REGISTRY:
        from backend.app.hands.tool_decorator import tool

        @tool(name=tool_name, risk_level="auto", tags=["test"])
        def _test_decorator_smoke_tool_xyz(city: str, days: int = 3) -> str:
            """Get weather forecast for a city."""
            return f"Weather for {city} over {days} days"

    assert tool_name in REGISTRY
    schema = REGISTRY[tool_name]["parameters"]
    assert schema["properties"]["city"]["type"] == "string"
    assert schema["properties"]["days"]["type"] == "integer"
    assert "city" in schema["required"]
    assert "days" not in schema["required"]  # has default value
