"""Built-in tools registered at import time (Phase 0–2)."""
from __future__ import annotations

from datetime import UTC, datetime


def register_builtin_tools() -> None:
    """Register core tools. Called once from registry after `register` exists."""
    from .registry import register

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

    register(
        {
            "name": "android_open",
            "description": (
                "Launch an intent or deep-link on the requesting Android client. "
                "Pass a URL (https://...), a market link (market://...), or an app "
                "package name (e.g. 'com.google.android.youtube')."
            ),
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "confirm_once",
            "executor": "client",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": (
                            "A http(s) URL, a market:// URL, or an Android app "
                            "package name to open via ACTION_VIEW."
                        ),
                    }
                },
                "required": ["target"],
            },
            "returns": {"type": "object", "properties": {"result": {"type": "object"}}},
            "scopes": ["android:open"],
            "tags": ["hands", "android"],
        },
    )

    register(
        {
            "name": "windows_open",
            "description": (
                "Open a URL, local file, or application on the requesting Windows "
                "client. Pass a URL (https://...), an absolute file/folder path, or "
                "an installed app name (e.g. 'notepad', 'calc', 'spotify')."
            ),
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "confirm_once",
            "executor": "client",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "URL, absolute file/folder path, or app name to open.",
                    }
                },
                "required": ["target"],
            },
            "returns": {"type": "object", "properties": {"result": {"type": "object"}}},
            "scopes": ["windows:open"],
            "tags": ["hands", "windows"],
        },
    )

    register(
        {
            "name": "windows_system_control",
            "description": (
                "Execute an OS-level system command on the requesting Windows client. "
                "Valid commands are: 'mute', 'unmute', 'volume_up', 'volume_down', 'lock_screen'."
            ),
            "version": "1.0.0",
            "phase": 2,
            "risk_level": "auto",
            "executor": "client",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute (e.g., mute, lock_screen).",
                    }
                },
                "required": ["command"],
            },
            "returns": {"type": "object", "properties": {"result": {"type": "object"}}},
            "scopes": ["windows:system"],
            "tags": ["hands", "windows", "system"],
        },
    )

    from .tools.velocity_build import register_velocity_build

    register_velocity_build()

