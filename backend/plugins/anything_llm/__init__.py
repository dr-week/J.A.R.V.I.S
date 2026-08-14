"""AnythingLLM RAG Knowledge Base Plugin (Zero-Code REST Sidecar).

Enables full RAG capabilities (document ingestion, vector search, chunking, workspace chat)
via self-hosted AnythingLLM Docker sidecar or REST endpoint per docs/OSS.md and docs/GITHUB_INTEGRATIONS.md
(Pattern 3: Docker Sidecar + REST call).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import httpx

from backend.app.hands import registry

ANYTHINGLLM_DEFAULT_URL = "http://localhost:3001"
ANYTHINGLLM_DEFAULT_WORKSPACE = "default"


def _get_base_url(url_override: str = "") -> str:
    """Resolve normalized AnythingLLM base URL."""
    url = (
        url_override
        or os.environ.get("ANYTHINGLLM_URL")
        or os.environ.get("JARVIS_ANYTHINGLLM_URL")
        or os.environ.get("ANYTHING_LLM_URL")
        or ANYTHINGLLM_DEFAULT_URL
    ).strip()
    return url.rstrip("/")


def _get_api_key(api_key_override: str = "") -> str:
    """Resolve AnythingLLM API key from parameter or environment."""
    return (
        api_key_override
        or os.environ.get("ANYTHINGLLM_API_KEY")
        or os.environ.get("JARVIS_ANYTHINGLLM_API_KEY")
        or os.environ.get("ANYTHING_LLM_API_KEY")
        or ""
    ).strip()


def _get_workspace(workspace_override: str = "") -> str:
    """Resolve AnythingLLM target workspace slug."""
    return (
        workspace_override
        or os.environ.get("ANYTHINGLLM_WORKSPACE")
        or os.environ.get("JARVIS_ANYTHINGLLM_WORKSPACE")
        or os.environ.get("ANYTHING_LLM_WORKSPACE")
        or ANYTHINGLLM_DEFAULT_WORKSPACE
    ).strip()


def _build_headers(api_key: str = "") -> dict[str, str]:
    """Construct HTTP headers with optional Bearer authentication."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "Jarvis-Brain",
    }
    key = _get_api_key(api_key)
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


async def anythingllm_query(
    query: str,
    workspace: str = "",
    mode: str = "query",
    url: str = "",
    api_key: str = "",
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Execute a semantic RAG query or chat against an AnythingLLM workspace.

    Args:
        query: The question or search text.
        workspace: Target workspace slug (default: 'default').
        mode: Query mode: 'query' (pure vector search RAG) or 'chat' (conversational RAG).
        url: Optional custom AnythingLLM base URL override.
        api_key: Optional custom API key override.
        timeout: Request timeout in seconds.

    Returns:
        Structured response dictionary containing response text, sources, and query metadata.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return {"error": "Search query cannot be empty."}

    base_url = _get_base_url(url)
    target_workspace = _get_workspace(workspace)
    endpoint = f"{base_url}/api/v1/workspace/{target_workspace}/chat"

    payload = {
        "message": clean_query,
        "mode": mode,
    }
    headers = _build_headers(api_key)
    headers["Content-Type"] = "application/json"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        text_response = (
            data.get("textResponse")
            or data.get("response")
            or data.get("message")
            or ""
        )
        sources = data.get("sources", [])

        return {
            "status": "ok",
            "query": clean_query,
            "workspace": target_workspace,
            "mode": mode,
            "response": text_response,
            "sources": sources,
            "raw": data,
        }
    except Exception as exc:
        return {
            "status": "error",
            "query": clean_query,
            "workspace": target_workspace,
            "error": f"AnythingLLM query request failed: {exc}. Ensure AnythingLLM sidecar is running at {base_url}.",
        }


async def anythingllm_upload_doc(
    file_path: str = "",
    text_content: str = "",
    doc_name: str = "",
    workspace: str = "",
    url: str = "",
    api_key: str = "",
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Upload or ingest a document/text into AnythingLLM RAG knowledge base.

    Args:
        file_path: Path to local document file to upload (PDF, TXT, MD, DOCX, etc.).
        text_content: Raw text content to ingest directly.
        doc_name: Document name/title for raw text or override filename.
        workspace: Target workspace slug (default: 'default').
        url: Optional custom AnythingLLM base URL override.
        api_key: Optional custom API key override.
        timeout: Request timeout in seconds.

    Returns:
        Structured result dictionary indicating upload status and response metadata.
    """
    clean_file_path = (file_path or "").strip()
    clean_text = (text_content or "").strip()

    if not clean_file_path and not clean_text:
        return {"error": "Must provide either file_path or text_content."}

    base_url = _get_base_url(url)
    target_workspace = _get_workspace(workspace)
    headers = _build_headers(api_key)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if clean_file_path:
                p = Path(clean_file_path)
                if not p.exists() or not p.is_file():
                    return {"error": f"File not found: {clean_file_path}"}

                upload_endpoint = f"{base_url}/api/v1/document/upload"
                file_bytes = p.read_bytes()
                name = doc_name.strip() or p.name

                files = {"file": (name, file_bytes)}
                resp = await client.post(upload_endpoint, files=files, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                resolved_name = name
            else:
                raw_endpoint = f"{base_url}/api/v1/document/raw-text"
                resolved_name = (doc_name or "document.txt").strip()
                headers["Content-Type"] = "application/json"
                payload = {
                    "textContent": clean_text,
                    "docName": resolved_name,
                }
                resp = await client.post(raw_endpoint, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

        return {
            "status": "uploaded",
            "workspace": target_workspace,
            "doc_name": resolved_name,
            "response": data,
        }
    except Exception as exc:
        return {
            "status": "error",
            "workspace": target_workspace,
            "error": f"AnythingLLM upload request failed: {exc}. Ensure AnythingLLM sidecar is running at {base_url}.",
        }


# Register tools into Hands registry
if "anythingllm_query" not in registry.REGISTRY:
    registry.register(
        {
            "name": "anythingllm_query",
            "description": (
                "Query self-hosted AnythingLLM RAG knowledge base sidecar for document retrieval and context."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question or search query for the RAG knowledge base.",
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Target AnythingLLM workspace slug (default: 'default').",
                    },
                    "mode": {
                        "type": "string",
                        "description": "Query mode: 'query' (pure RAG context) or 'chat' (conversational).",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional custom AnythingLLM base URL override.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional custom AnythingLLM API key override.",
                    },
                },
                "required": ["query"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "query": {"type": "string"},
                    "workspace": {"type": "string"},
                    "mode": {"type": "string"},
                    "response": {"type": "string"},
                    "sources": {"type": "array"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["rag:read", "knowledge:read"],
            "tags": ["rag", "anythingllm", "knowledge_base", "documents", "zero-code"],
        },
        anythingllm_query,
    )


if "anythingllm_upload_doc" not in registry.REGISTRY:
    registry.register(
        {
            "name": "anythingllm_upload_doc",
            "description": (
                "Upload or ingest a document/text into self-hosted AnythingLLM RAG knowledge base sidecar."
            ),
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "confirm_once",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local file path to document to upload (PDF, TXT, MD, DOCX, etc.).",
                    },
                    "text_content": {
                        "type": "string",
                        "description": "Raw text content to ingest into the knowledge base directly.",
                    },
                    "doc_name": {
                        "type": "string",
                        "description": "Document name or title (e.g. 'manual.txt').",
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Target AnythingLLM workspace slug (default: 'default').",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional custom AnythingLLM base URL override.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional custom AnythingLLM API key override.",
                    },
                },
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "workspace": {"type": "string"},
                    "doc_name": {"type": "string"},
                    "response": {"type": "object"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["rag:write", "knowledge:write"],
            "tags": ["rag", "anythingllm", "knowledge_base", "documents", "zero-code"],
        },
        anythingllm_upload_doc,
    )
