"""Core utility tools: hello_world, get_current_time, dangerous_demo.

Single responsibility: brain-executor tools with no OS or client side effects.
"""
from __future__ import annotations

from datetime import UTC, datetime


def register_core_tools() -> None:
    """Register core utility tools. Called from builtin_tools.register_builtin_tools()."""
    from ..registry import register

    def _hello_world(name: str = "world") -> str:
        return f"Hello, {name}! The tool registry is working."

    def _get_time() -> str:
        return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    def _dangerous_demo(message: str = "test", api_key: str = "") -> str:
        return f"Confirmed action executed: {message}"

    register(
        {
            "name": "hello_world",
            "description": "Returns a greeting. Used to verify the tool registry works.",
            "version": "1.0.0",
            "phase": 0,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Name to greet"}},
                "required": [],
            },
            "returns": {"type": "object", "properties": {"result": {"type": "string"}}},
            "scopes": [],
            "tags": ["test"],
        },
        _hello_world,
    )

    register(
        {
            "name": "get_current_time",
            "description": "Returns the current UTC time. Use when the user asks what time or date it is.",
            "version": "1.0.0",
            "phase": 0,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "returns": {"type": "object", "properties": {"result": {"type": "string"}}},
            "scopes": [],
            "tags": ["utility"],
        },
        _get_time,
    )

    register(
        {
            "name": "dangerous_demo",
            "description": "Demo high-risk tool. Requires user confirmation before running.",
            "version": "1.0.0",
            "phase": 0,
            "risk_level": "confirm_always",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Payload to echo after confirm"},
                    "api_key": {"type": "string", "description": "Sensitive field (redacted in logs)"},
                },
                "required": ["message"],
            },
            "returns": {"type": "object", "properties": {"result": {"type": "string"}}},
            "scopes": [],
            "tags": ["test", "security"],
        },
        _dangerous_demo,
    )
