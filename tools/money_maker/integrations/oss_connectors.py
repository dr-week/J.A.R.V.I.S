"""Open-Source Backend Connectors for Jarvis Money Maker.

Connects to lightweight open-source backends:
- PocketBase / Supabase (Realtime Database & Auth)
- MedusaJS (Indian D2C E-commerce Catalog Sync)
- Webhook Dispatcher (Automated alerting to WhatsApp / Telegram)
"""
import json
import requests
from typing import Dict, Any, Optional

def dispatch_webhook(webhook_url: str, payload: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
    """Dispatches a structured JSON event to an external webhook (n8n, Zapier, Telegram bot, Discord)."""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )
        return {
            "status": "success",
            "status_code": response.status_code,
            "response": response.text[:200]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def format_whatsapp_deal_alert(deal_title: str, deal_url: str, original_price: str, loot_price: str) -> str:
    """Formats high-converting Indian WhatsApp/Telegram broadcast message for affiliate loot deals."""
    return (
        f"🔥 *LOOT DEAL ALERT!* 🔥\n\n"
        f"📦 *Product:* {deal_title}\n"
        f"❌ *MRP:* ~{original_price}~\n"
        f"✅ *Deal Price:* *{loot_price}* (Huge Discount!)\n\n"
        f"🛒 *Grab Now:* {deal_url}\n\n"
        f"⚡ _Verified by Jarvis Money Maker Radar_"
    )
