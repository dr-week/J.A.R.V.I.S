"""Jarvis Brain — configuration.

All settings come from environment variables (or .env file).
No hardcoded secrets; see .env.example for documentation.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from repo root (two levels up from this file)
_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Identity ────────────────────────────────────────────────────────────────
    ASSISTANT_NAME: str = Field(default="Jarvis")

    # ── LLM ─────────────────────────────────────────────────────────────────────
    JARVIS_LLM_PROVIDER: str = Field(default="gemini")
    GEMINI_API_KEY: str = Field(default="")
    JARVIS_LLM_MODEL: str = Field(default="gemini-2.0-flash")
    JARVIS_LLM_BASE_URL: str = Field(default="")
    JARVIS_LLM_API_KEY: str = Field(default="")
    JARVIS_LITELLM_MODEL: str = Field(default="")
    JARVIS_LITELLM_BASE_URL: str = Field(default="")
    JARVIS_LITELLM_API_KEY: str = Field(default="")

    # ── Brain server ─────────────────────────────────────────────────────────────
    JARVIS_ENV: str = Field(default="development")
    JARVIS_HOST: str = Field(default="0.0.0.0")
    JARVIS_PORT: int = Field(default=8787)
    JARVIS_DATA_DIR: str = Field(default=str(_ROOT / "backend" / "data"))
    JARVIS_CORS_ORIGINS: str = Field(default="*")

    # ── Auth / pairing ───────────────────────────────────────────────────────────
    JARVIS_PAIRING_SECRET: str = Field(default="change-me")
    JARVIS_JWT_SECRET: str = Field(default="change-me")
    JARVIS_JWT_EXPIRE_DAYS: int = Field(default=30)

    # ── Learning ─────────────────────────────────────────────────────────────────
    LEARNING_ENABLED: bool = Field(default=True)
    LEARNING_MIN_OCCURRENCES: int = Field(default=3)

    # ── Home Assistant bridge (Phase 5 house Hands) ──────────────────────────────
    JARVIS_HA_URL: str = Field(default="")
    JARVIS_HA_TOKEN: str = Field(default="")
    JARVIS_HA_ENTITY: str = Field(default="light.living_room")

    # ── Velocity app builder ───────────────────────────────────────────────────
    JARVIS_VELOCITY_URL: str = Field(default="http://127.0.0.1:5174")
    JARVIS_VELOCITY_ROOT: str = Field(default="")

    @field_validator("JARVIS_ENV")
    @classmethod
    def lower_env(cls, v: str) -> str:
        return v.lower()


settings = Settings()

# Re-export variables to avoid breaking existing imports in the rest of the codebase
ASSISTANT_NAME = settings.ASSISTANT_NAME

LLM_PROVIDER = settings.JARVIS_LLM_PROVIDER
GEMINI_API_KEY = settings.GEMINI_API_KEY
LLM_MODEL = settings.JARVIS_LLM_MODEL
LLM_BASE_URL = settings.JARVIS_LLM_BASE_URL
LLM_API_KEY = settings.JARVIS_LLM_API_KEY
LITELLM_MODEL = settings.JARVIS_LITELLM_MODEL
LITELLM_BASE_URL = settings.JARVIS_LITELLM_BASE_URL
LITELLM_API_KEY = settings.JARVIS_LITELLM_API_KEY

ENVIRONMENT = settings.JARVIS_ENV
HOST = settings.JARVIS_HOST
PORT = settings.JARVIS_PORT

DATA_DIR = Path(settings.JARVIS_DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "brain.db"

PAIRING_SECRET = settings.JARVIS_PAIRING_SECRET
JWT_SECRET = settings.JARVIS_JWT_SECRET
JWT_EXPIRE_DAYS = settings.JARVIS_JWT_EXPIRE_DAYS

if ENVIRONMENT == "production" and (PAIRING_SECRET == "change-me" or JWT_SECRET == "change-me"):
    raise ValueError("SECURITY ERROR: Default secrets are not allowed when JARVIS_ENV=production. Please set JARVIS_PAIRING_SECRET and JARVIS_JWT_SECRET in .env")

LEARNING_ENABLED = settings.LEARNING_ENABLED
LEARNING_MIN_OCCURRENCES = settings.LEARNING_MIN_OCCURRENCES

HA_URL = settings.JARVIS_HA_URL
HA_TOKEN = settings.JARVIS_HA_TOKEN
HA_ENTITY = settings.JARVIS_HA_ENTITY

VELOCITY_URL = settings.JARVIS_VELOCITY_URL
VELOCITY_ROOT = settings.JARVIS_VELOCITY_ROOT


def llm_ready() -> bool:
    """True if the minimum LLM config is present."""
    if LLM_PROVIDER == "gemini":
        return bool(GEMINI_API_KEY)
    if LLM_PROVIDER in ("openai", "ollama"):
        # Local servers (LM Studio) often need only base URL; key optional
        return bool(LLM_BASE_URL) or bool(LLM_API_KEY)
    if LLM_PROVIDER == "litellm":
        return bool(LITELLM_BASE_URL) or bool(LITELLM_API_KEY)
    return False
