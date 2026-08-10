"""API — /health endpoint."""
from fastapi import APIRouter

from .. import config
from ..soul.persona import get_assistant_name

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "assistant_name": get_assistant_name(),
        "llm_provider": config.LLM_PROVIDER,
        "llm_model": config.LLM_MODEL,
        "llm_ready": config.llm_ready(),
        "learning_enabled": config.LEARNING_ENABLED,
        "version": "0.1.0",
    }
