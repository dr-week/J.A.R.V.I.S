"""Jarvis Brain — configuration.

All settings come from environment variables (or .env file).
No hardcoded secrets; see .env.example for documentation.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root (two levels up from this file)
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()

def _get_int(key: str, default: int) -> int:
    val = _get(key)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


# ── Identity ────────────────────────────────────────────────────────────────
ASSISTANT_NAME: str = _get("ASSISTANT_NAME", "Jarvis")

# ── LLM ─────────────────────────────────────────────────────────────────────
LLM_PROVIDER: str = _get("JARVIS_LLM_PROVIDER", "gemini")          # gemini | openai | ollama
GEMINI_API_KEY: str = _get("GEMINI_API_KEY", "")
LLM_MODEL: str = _get("JARVIS_LLM_MODEL", "gemini-2.0-flash")
LLM_BASE_URL: str = _get("JARVIS_LLM_BASE_URL", "")
LLM_API_KEY: str = _get("JARVIS_LLM_API_KEY", "")

# ── Brain server ─────────────────────────────────────────────────────────────
ENVIRONMENT: str = _get("JARVIS_ENV", "development").lower()
HOST: str = _get("JARVIS_HOST", "0.0.0.0")
PORT: int = _get_int("JARVIS_PORT", 8787)
DATA_DIR: Path = Path(_get("JARVIS_DATA_DIR", str(_ROOT / "backend" / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH: Path = DATA_DIR / "brain.db"

# ── Auth / pairing ───────────────────────────────────────────────────────────
PAIRING_SECRET: str = _get("JARVIS_PAIRING_SECRET", "change-me")
JWT_SECRET: str = _get("JARVIS_JWT_SECRET", "change-me")
JWT_EXPIRE_DAYS: int = _get_int("JARVIS_JWT_EXPIRE_DAYS", 30)

if ENVIRONMENT == "production" and (PAIRING_SECRET == "change-me" or JWT_SECRET == "change-me"):
    raise ValueError("SECURITY ERROR: Default secrets are not allowed when JARVIS_ENV=production. Please set JARVIS_PAIRING_SECRET and JARVIS_JWT_SECRET in .env")

# ── Learning ─────────────────────────────────────────────────────────────────
LEARNING_ENABLED: bool = _get("LEARNING_ENABLED", "true").lower() in ("true", "1", "yes")
LEARNING_MIN_OCCURRENCES: int = _get_int("LEARNING_MIN_OCCURRENCES", 3)

# ── Home Assistant bridge (Phase 5 house Hands) ──────────────────────────────
HA_URL: str = _get("JARVIS_HA_URL", "")          # e.g. http://192.168.1.10:8123
HA_TOKEN: str = _get("JARVIS_HA_TOKEN", "")      # long-lived HA access token
HA_ENTITY: str = _get("JARVIS_HA_ENTITY", "light.living_room")

# ── Derived ──────────────────────────────────────────────────────────────────
def llm_ready() -> bool:
    """True if the minimum LLM config is present."""
    if LLM_PROVIDER == "gemini":
        return bool(GEMINI_API_KEY)
    if LLM_PROVIDER in ("openai", "ollama"):
        return bool(LLM_BASE_URL or LLM_API_KEY)
    return False
