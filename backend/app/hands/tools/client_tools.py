"""Client-side OS tools: android_open, windows_open, windows_system_control.

Single responsibility: schema-only registrations for tools executed on the requesting
device (phone / desktop). No Python executor — execution is dispatched by the registry
to the connected client over WebSocket.
"""
from __future__ import annotations


def register_client_tools() -> None:
    """Register client-executor OS tools. Called from builtin_tools.register_builtin_tools()."""
    from ..registry import register

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
