"""Jarvis Brain — FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .api import chat, hands, health, pair, sessions, soul, sync, tools
from .soul.memory import init_db
from .soul.persona import get_assistant_name

# Default secrets shipped in config.py. If still in use, operators may be
# running production with stub credentials.
_DEFAULT_SECRETS = {
    "PAIRING_SECRET": "JARVIS_PAIRING_SECRET",
    "JWT_SECRET": "JARVIS_JWT_SECRET",
}


def _warn_default_secrets() -> None:
    """Print a clear WARNING when a default (stub) secret is still in use.

    Only the env-var name is logged, never the secret value itself.
    """
    defaults_in_use = []
    for attr, env_key in _DEFAULT_SECRETS.items():
        if getattr(config, attr) == "change-me":
            defaults_in_use.append(env_key)
    if not defaults_in_use:
        return
    print("! " * 24)
    print("  SECURITY WARNING: default secret(s) still in use:")
    for env_key in defaults_in_use:
        print(f"    - {env_key} is set to the insecure default 'change-me'")
    print("  Set a strong, unique value in your .env file before going to")
    print("  production. See docs/SECURITY.md for details.")
    print("! " * 24)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    from .hands.registry import discover_plugins
    discover_plugins()
    
    name = get_assistant_name()
    print(f"\n{'='*50}")
    print(f"  {name} Brain starting up")
    print(f"  LLM: {config.LLM_PROVIDER} / {config.LLM_MODEL}")
    print(f"  LLM ready: {config.llm_ready()}")
    print(f"  Learning: {'enabled' if config.LEARNING_ENABLED else 'disabled'}")
    print(f"  DB: {config.DB_PATH}")
    print(f"{'='*50}\n")
    _warn_default_secrets()
    yield
    print(f"\n{name} Brain shutting down. Goodbye.\n")


app = FastAPI(
    title="Jarvis Brain",
    description="Central AI brain — Soul + Mind + Hands. See /docs for API.",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins = [origin.strip() for origin in config._get("JARVIS_CORS_ORIGINS", "*").split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True if "*" not in cors_origins else False,
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(soul.router)
app.include_router(sync.router)
app.include_router(pair.router)
app.include_router(tools.router)
app.include_router(hands.router)


@app.get("/")
async def root():
    name = get_assistant_name()
    return {
        "name": name,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0",
    }
