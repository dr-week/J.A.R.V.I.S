"""Smoke: velocity_build registers; openai tools builder is importable."""
from backend.app.hands.registry import REGISTRY


def test_velocity_build_registered():
    assert "velocity_build" in REGISTRY
    tool = REGISTRY["velocity_build"]
    assert tool["risk_level"] == "confirm_always"
    assert "app_description" in tool["parameters"]["properties"]


def test_openai_tools_shape():
    from backend.app.mind.openai_loop import _openai_tools

    tools = _openai_tools()
    assert isinstance(tools, list)
    assert any(t["function"]["name"] == "velocity_build" for t in tools)
