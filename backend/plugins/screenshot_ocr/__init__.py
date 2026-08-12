"""Screenshot + OCR plugin — mss for capture, pytesseract for text extraction.

Saves screenshots to a local directory. Self-registers when
``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.hands import registry

try:
    import mss
    _HAS_MSS = True
except ImportError:
    _HAS_MSS = False

try:
    import pytesseract
    from PIL import Image
    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False

# Screenshots directory
_SCREENSHOTS_DIR = Path(os.environ.get("JARVIS_SCREENSHOTS_DIR", "screenshots"))
_SCREENSHOTS_DIR.mkdir(exist_ok=True)


def _screenshot_take() -> dict[str, Any]:
    """Take a screenshot and save to disk."""
    if not _HAS_MSS:
        return {"error": "mss not installed. Run: pip install mss"}
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = _SCREENSHOTS_DIR / filename
    with mss.mss() as sct:
        # Capture primary monitor
        monitor = sct.monitors[1]  # primary
        sct_img = sct.grab(monitor)
        # Save using mss built-in
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=str(filepath))
    return {
        "file": str(filepath.resolve()),
        "size": f"{sct_img.size.width}x{sct_img.size.height}",
        "timestamp": timestamp,
    }


def _screenshot_ocr() -> dict[str, Any]:
    """Take a screenshot and extract text via OCR."""
    if not _HAS_MSS:
        return {"error": "mss not installed. Run: pip install mss"}
    if not _HAS_OCR:
        return {"error": "pytesseract/Pillow not installed. Run: pip install pytesseract Pillow"}
    # Take screenshot first
    shot = _screenshot_take()
    if "error" in shot:
        return shot
    try:
        img = Image.open(shot["file"])
        text = pytesseract.image_to_string(img)
        return {
            "file": shot["file"],
            "text": text.strip()[:5000],  # cap at 5k chars
            "char_count": len(text.strip()),
        }
    except Exception as exc:
        return {"file": shot["file"], "error": f"OCR failed: {exc}"}


# ── Register ────────────────────────────────────────────────────

registry.register(
    {
        "name": "screenshot_take", "description": "Take a screenshot of the primary monitor and save to disk.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"file": {"type": "string"}, "size": {"type": "string"}}},
        "scopes": ["system:read"], "tags": ["utility", "screenshot"],
    }, _screenshot_take,
)

registry.register(
    {
        "name": "screenshot_ocr", "description": "Take a screenshot and extract all visible text via OCR.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "object", "properties": {"file": {"type": "string"}, "text": {"type": "string"}}},
        "scopes": ["system:read"], "tags": ["utility", "screenshot", "ocr"],
    }, _screenshot_ocr,
)
