"""AnythingLLM HTTP API Client.

Handles URL resolution, authentication headers, document uploading,
and conversational/vector querying against an AnythingLLM instance.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import httpx

ANYTHINGLLM_DEFAULT_URL = "http://localhost:3001"
ANYTHINGLLM_DEFAULT_WORKSPACE = "default"


def get_base_url(url_override: str = "") -> str:
    """Resolve normalized AnythingLLM base URL."""
    url = (
        url_override
        or os.environ.get("ANYTHINGLLM_URL")
        or os.environ.get("JARVIS_ANYTHINGLLM_URL")
        or os.environ.get("ANYTHING_LLM_URL")
        or ANYTHINGLLM_DEFAULT_URL
    ).strip()
    return url.rstrip("/")


def get_api_key(api_key_override: str = "") -> str:
    """Resolve AnythingLLM API key from parameter or environment."""
    return (
        api_key_override
        or os.environ.get("ANYTHINGLLM_API_KEY")
        or os.environ.get("JARVIS_ANYTHINGLLM_API_KEY")
        or os.environ.get("ANYTHING_LLM_API_KEY")
        or ""
    ).strip()


def get_workspace(workspace_override: str = "") -> str:
    """Resolve AnythingLLM target workspace slug."""
    return (
        workspace_override
        or os.environ.get("ANYTHINGLLM_WORKSPACE")
        or os.environ.get("JARVIS_ANYTHINGLLM_WORKSPACE")
        or os.environ.get("ANYTHING_LLM_WORKSPACE")
        or ANYTHINGLLM_DEFAULT_WORKSPACE
    ).strip()


def build_headers(api_key: str = "") -> dict[str, str]:
    """Construct HTTP headers with optional Bearer authentication."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "Jarvis-Brain",
    }
    key = get_api_key(api_key)
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


async def execute_query(
    query: str,
    workspace: str = "",
    mode: str = "query",
    url: str = "",
    api_key: str = "",
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Execute a semantic RAG query or chat against an AnythingLLM workspace."""
    if not query or not query.strip():
        return {"status": "error", "error": "Query cannot be empty."}

    base_url = get_base_url(url)
    target_workspace = get_workspace(workspace)
    headers = build_headers(api_key)

    endpoint = f"{base_url}/api/v1/workspace/{target_workspace}/chat"
    payload = {
        "message": query,
        "mode": mode if mode in ("query", "chat") else "query",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text_response = (
                    data.get("textResponse")
                    or data.get("response")
                    or data.get("message")
                    or str(data)
                )
                sources = data.get("sources", [])
                return {
                    "status": "ok",
                    "query": query,
                    "workspace": target_workspace,
                    "mode": mode,
                    "response": text_response,
                    "sources": sources,
                }
            elif resp.status_code == 404:
                return {
                    "status": "error",
                    "query": query,
                    "workspace": target_workspace,
                    "error": f"Workspace ''{target_workspace}'' not found at {base_url}.",
                }
            else:
                return {
                    "status": "error",
                    "query": query,
                    "workspace": target_workspace,
                    "status_code": resp.status_code,
                    "error": f"AnythingLLM returned HTTP {resp.status_code}: {resp.text[:300]}",
                }
    except Exception as exc:
        return {
            "status": "error",
            "query": query,
            "workspace": target_workspace,
            "error": f"AnythingLLM request failed: {exc}. Ensure AnythingLLM sidecar is running at {base_url}.",
        }


async def execute_upload(
    file_path: str = "",
    text_content: str = "",
    doc_name: str = "",
    workspace: str = "",
    url: str = "",
    api_key: str = "",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Upload or ingest a document/text into an AnythingLLM workspace."""
    if not file_path and not text_content:
        return {"status": "error", "error": "Must provide either file_path or text_content."}

    base_url = get_base_url(url)
    target_workspace = get_workspace(workspace)
    headers = build_headers(api_key)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if text_content:
                upload_endpoint = f"{base_url}/api/v1/document/raw-text"
                payload = {
                    "textContent": text_content,
                    "docName": doc_name or "injected_text.txt",
                }
                resp = await client.post(upload_endpoint, json=payload, headers=headers)
            else:
                p = Path(file_path)
                if not p.exists() or not p.is_file():
                    return {"status": "error", "error": f"File not found: {file_path}"}
                upload_endpoint = f"{base_url}/api/v1/document/upload"
                with open(p, "rb") as f:
                    files = {"file": (p.name, f, "application/octet-stream")}
                    resp = await client.post(upload_endpoint, files=files, headers=headers)

            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "status": "uploaded",
                    "workspace": target_workspace,
                    "doc_name": doc_name or (Path(file_path).name if file_path else "raw_text"),
                    "response": data,
                }
            else:
                return {
                    "status": "error",
                    "workspace": target_workspace,
                    "status_code": resp.status_code,
                    "error": f"AnythingLLM upload returned HTTP {resp.status_code}: {resp.text[:300]}",
                }
    except Exception as exc:
        return {
            "status": "error",
            "workspace": target_workspace,
            "error": f"AnythingLLM upload request failed: {exc}. Ensure AnythingLLM sidecar is running at {base_url}.",
        }
