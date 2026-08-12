"""Media control plugin — Windows audio control via pycaw.

Controls system volume, mute, and (future) media playback.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any

from backend.app.hands import registry

# Lazy import — pycaw is Windows-only
_HAS_PYCAW = False
_volume_interface = None

try:
    from ctypes import cast, POINTER
    import comtypes
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    comtypes.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
    _volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
    _HAS_PYCAW = True
except Exception:
    pass


def _media_volume_get() -> dict[str, Any]:
    """Get current system volume level (0-100)."""
    if not _HAS_PYCAW or not _volume_interface:
        return {"error": "pycaw not available. Windows only. Run: pip install pycaw comtypes"}
    try:
        level = _volume_interface.GetMasterVolumeLevelScalar()
        muted = _volume_interface.GetMute()
        return {"volume": round(level * 100), "muted": bool(muted)}
    except Exception as exc:
        return {"error": str(exc)}


def _media_volume_set(level: int) -> dict[str, Any]:
    """Set system volume to a level between 0-100."""
    if not _HAS_PYCAW or not _volume_interface:
        return {"error": "pycaw not available. Windows only. Run: pip install pycaw comtypes"}
    clamped = max(0, min(100, level))
    try:
        _volume_interface.SetMasterVolumeLevelScalar(clamped / 100.0, None)
        return {"volume": clamped, "set": True}
    except Exception as exc:
        return {"error": str(exc)}


def _media_mute_toggle() -> dict[str, Any]:
    """Toggle system mute on/off."""
    if not _HAS_PYCAW or not _volume_interface:
        return {"error": "pycaw not available. Windows only. Run: pip install pycaw comtypes"}
    try:
        current = _volume_interface.GetMute()
        _volume_interface.SetMute(not current, None)
        return {"muted": not current, "toggled": True}
    except Exception as exc:
        return {"error": str(exc)}


# ── Register ────────────────────────────────────────────────────

registry.register(
    {
        "name": "media_volume_get", "description": "Get the current system volume level (0-100) and mute state.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"volume": {"type": "integer"}, "muted": {"type": "boolean"}}},
        "scopes": ["system:read"], "tags": ["utility", "media", "audio"],
    }, _media_volume_get,
)

registry.register(
    {
        "name": "media_volume_set", "description": "Set the system volume to a level between 0-100.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {"level": {"type": "integer"}}, "required": ["level"]},
        "returns": {"type": "object", "properties": {"volume": {"type": "integer"}, "set": {"type": "boolean"}}},
        "scopes": ["system:write"], "tags": ["utility", "media", "audio"],
    }, _media_volume_set,
)

registry.register(
    {
        "name": "media_mute_toggle", "description": "Toggle system audio mute on/off.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"muted": {"type": "boolean"}, "toggled": {"type": "boolean"}}},
        "scopes": ["system:write"], "tags": ["utility", "media", "audio"],
    }, _media_mute_toggle,
)
