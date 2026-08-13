"""Secrets plugin — OS keychain access via keyring.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry

try:
    import keyring
    _HAS_KEYRING = True
except ImportError:
    _HAS_KEYRING = False

_SERVICE_NAME = "jarvis_brain"


def _secret_store(key: str, value: str) -> dict[str, Any]:
    """Securely store a secret in OS keychain."""
    if not _HAS_KEYRING:
        return {"error": "keyring is not installed. Run: pip install keyring"}
    try:
        keyring.set_password(_SERVICE_NAME, key, value)
        return {"stored": True, "key": key}
    except Exception as exc:
        return {"error": str(exc)}


def _secret_get(key: str) -> dict[str, Any]:
    """Retrieve a secret from OS keychain."""
    if not _HAS_KEYRING:
        return {"error": "keyring is not installed. Run: pip install keyring"}
    try:
        val = keyring.get_password(_SERVICE_NAME, key)
        if val is None:
            return {"error": f"Secret '{key}' not found."}
        return {"key": key, "value": val}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "secret_store",
        "description": "Securely store an API key or password in the system OS keychain.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_always",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["key", "value"],
        },
        "returns": {"type": "object", "properties": {"stored": {"type": "boolean"}}},
        "scopes": ["secrets:write"],
        "tags": ["security", "secrets"],
    },
    _secret_store,
)

registry.register(
    {
        "name": "secret_get",
        "description": "Retrieve a secret or API key from the system OS keychain.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_always",
        "executor": "brain",
        "parameters": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]},
        "returns": {"type": "object", "properties": {"value": {"type": "string"}}},
        "scopes": ["secrets:read"],
        "tags": ["security", "secrets"],
    },
    _secret_get,
)
