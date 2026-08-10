import logging

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter()

# In a real app, this would push to a Redis PubSub or Memory Queue for SSE broadcast
@router.post("/internal/webhook/velocity")
async def velocity_webhook(request: Request):
    """Webhook for Velocity build progress. JSON: app_id, status, message."""
    try:
        payload = await request.json()
        app_id = payload.get("app_id")
        status = payload.get("status")
        message = payload.get("message")
        
        logger.info(f"[Velocity Webhook] App {app_id} status: {status} - {message}")
        
        # Here we would emit the event to the connected WebSocket clients
        # e.g., await sse_manager.broadcast({"type": "velocity_update", "data": payload})
        
        return {"success": True, "processed": True}
    except Exception as e:
        logger.error(f"Error processing velocity webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
