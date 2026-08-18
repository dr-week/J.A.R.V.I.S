"""API -- /chat endpoint (streaming SSE) and /ws WebSocket."""
from __future__ import annotations

import json
import typing
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .. import config
from ..mind.agent import stream_chat
from ..sync.manager import manager
from .pair import validate_token

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    session_id: str = ""
    device_id: str = ""
    surface: str = ""
    room: str = ""
    client_msg_id: str | None = None
    confirm_pending_tool: bool = False


@router.post("/chat")
async def chat(req: ChatRequest) -> typing.Any:
    """Send a message, get a streaming SSE response."""
    session_id = req.session_id or str(uuid.uuid4())

    async def event_stream() -> typing.Any:
        try:
            async for chunk in stream_chat(
                session_id,
                req.text,
                req.device_id,
                req.client_msg_id,
                req.confirm_pending_tool,
                surface=req.surface,
                room=req.room,
            ):
                payload = json.dumps({"chunk": chunk})
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            err_payload = json.dumps({"error": str(exc)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )


@router.websocket("/ws")
async def websocket_chat(ws: WebSocket) -> typing.Any:
    """WebSocket endpoint -- clients connect, register a device_id, and
    exchange JSON messages. Supports chat streaming plus device-bridge
    tool dispatch (Issue-032)."""
    
    token = ws.query_params.get("token")
    if not token:
        auth_header = ws.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            
    if token:
        info = validate_token(token)
        if not info:
            await ws.close(code=1008, reason="Invalid token")
            return
            
    await manager.connect(ws)
    authenticated = bool(token)
    
    try:
        while True:
            raw = await ws.receive_json()
            
            if not authenticated:
                msg_token = raw.get("token")
                if msg_token:
                    info = validate_token(msg_token)
                    if not info:
                        await ws.send_json({"type": "error", "message": "Invalid token"})
                        manager.disconnect(ws)
                        return
                    authenticated = True
                elif config.ENVIRONMENT == "production":
                    await ws.send_json({"type": "error", "message": "Unauthorized"})
                    manager.disconnect(ws)
                    return
                else:
                    authenticated = True

            msg_type = raw.get("type", "message")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue

            # Client handshake: bind this connection to a device_id so the
            # brain can route client-executor tools to it.
            if msg_type == "register":
                device_id = raw.get("device_id", "")
                manager.register_device(ws, device_id)
                await ws.send_json(
                    {"type": "registered", "device_id": device_id}
                )
                continue

            # Device bridge: client returns a tool execution result.
            if msg_type == "tool_result":
                request_id = raw.get("request_id", "")
                manager.resolve(request_id, raw)
                continue

            if msg_type == "message":
                text = raw.get("text", "")
                session_id = raw.get("session_id") or str(uuid.uuid4())
                device_id = raw.get("device_id", "")
                surface = raw.get("surface", "")
                room = raw.get("room", "")
                client_msg_id = raw.get("client_msg_id")
                confirm_pending = bool(raw.get("confirm_pending_tool", False))

                async for chunk in stream_chat(
                    session_id,
                    text,
                    device_id,
                    client_msg_id,
                    confirm_pending,
                    surface=surface,
                    room=room,
                ):
                    await ws.send_json({"type": "chunk", "session_id": session_id, "text": chunk})

                await ws.send_json({"type": "done", "session_id": session_id})

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as exc:
        try:
            await ws.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
        finally:
            manager.disconnect(ws)
