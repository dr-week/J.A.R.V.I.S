"""Email plugin — IMAP inbox + SMTP send via imapclient.

Reads config from environment variables. Self-registers when
``discover_plugins`` scans this package.
"""
from __future__ import annotations

import email
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from backend.app.hands import registry

# Lazy import — may not be installed in all environments
try:
    import imapclient  # noqa: F401
    _HAS_IMAP = True
except ImportError:
    _HAS_IMAP = False


def _get_config() -> dict[str, str]:
    """Read email config from env vars."""
    conf = {
        "imap_host": os.environ.get("EMAIL_IMAP_HOST", ""),
        "smtp_host": os.environ.get("EMAIL_SMTP_HOST", ""),
        "username": os.environ.get("EMAIL_USERNAME", ""),
        "password": os.environ.get("EMAIL_PASSWORD", ""),
        "smtp_port": int(os.environ.get("EMAIL_SMTP_PORT", "587")),
    }
    if not conf["username"] or not conf["password"]:
        raise ValueError(
            "Email not configured. Set EMAIL_IMAP_HOST, EMAIL_SMTP_HOST, "
            "EMAIL_USERNAME, EMAIL_PASSWORD in .env"
        )
    return conf


def _extract_body(msg: email.message.Message) -> str:
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")
    return ""


def _email_inbox(limit: int = 10) -> dict[str, Any]:
    """Fetch recent emails from inbox."""
    if not _HAS_IMAP:
        return {"error": "imapclient not installed. Run: pip install imapclient"}
    conf = _get_config()
    try:
        with imapclient.IMAPClient(conf["imap_host"], ssl=True) as client:
            client.login(conf["username"], conf["password"])
            client.select_folder("INBOX", readonly=True)
            uids = client.search(["ALL"])
            uids = uids[-limit:]  # most recent
            uids.reverse()
            messages = []
            if uids:
                raw = client.fetch(uids, ["ENVELOPE", "BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)]"])
                for uid, data in raw.items():
                    env = data.get(b"ENVELOPE")
                    if env:
                        sender = ""
                        if env.from_ and len(env.from_) > 0:
                            addr = env.from_[0]
                            sender = f"{addr.name.decode() if addr.name else ''} <{addr.mailbox.decode()}@{addr.host.decode()}>"
                        messages.append({
                            "uid": str(uid),
                            "subject": env.subject.decode() if env.subject else "(no subject)",
                            "from": sender,
                            "date": str(env.date) if env.date else "",
                        })
            return {"count": len(messages), "emails": messages}
    except Exception as exc:
        return {"error": str(exc)}


def _email_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Search emails by subject keyword."""
    if not _HAS_IMAP:
        return {"error": "imapclient not installed. Run: pip install imapclient"}
    conf = _get_config()
    try:
        with imapclient.IMAPClient(conf["imap_host"], ssl=True) as client:
            client.login(conf["username"], conf["password"])
            client.select_folder("INBOX", readonly=True)
            uids = client.search(["SUBJECT", query])
            uids = uids[-limit:]
            uids.reverse()
            messages = []
            if uids:
                raw = client.fetch(uids, ["ENVELOPE"])
                for uid, data in raw.items():
                    env = data.get(b"ENVELOPE")
                    if env:
                        messages.append({
                            "uid": str(uid),
                            "subject": env.subject.decode() if env.subject else "",
                            "date": str(env.date) if env.date else "",
                        })
            return {"count": len(messages), "emails": messages}
    except Exception as exc:
        return {"error": str(exc)}


def _email_read(uid: str) -> dict[str, Any]:
    """Read full email content by UID."""
    if not _HAS_IMAP:
        return {"error": "imapclient not installed. Run: pip install imapclient"}
    conf = _get_config()
    try:
        with imapclient.IMAPClient(conf["imap_host"], ssl=True) as client:
            client.login(conf["username"], conf["password"])
            client.select_folder("INBOX", readonly=True)
            raw = client.fetch([int(uid)], ["RFC822"])
            if int(uid) not in raw:
                raise ValueError(f"No email found with UID '{uid}'.")
            msg = email.message_from_bytes(raw[int(uid)][b"RFC822"])
            return {
                "uid": uid,
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "date": msg.get("Date", ""),
                "body": _extract_body(msg)[:5000],  # cap body length
            }
    except Exception as exc:
        return {"error": str(exc)}


def _email_send(to: str, subject: str, body: str) -> dict[str, Any]:
    """Send an email via SMTP."""
    conf = _get_config()
    try:
        msg = MIMEMultipart()
        msg["From"] = conf["username"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(conf["smtp_host"], conf["smtp_port"]) as server:
            server.starttls()
            server.login(conf["username"], conf["password"])
            server.send_message(msg)
        return {"sent": True, "to": to, "subject": subject}
    except Exception as exc:
        return {"error": str(exc)}


# ── Register tools ──────────────────────────────────────────────

registry.register(
    {
        "name": "email_inbox", "description": "Fetch the most recent emails from your inbox.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "emails": {"type": "array"}}},
        "scopes": ["email:read"], "tags": ["productivity", "email"],
    }, _email_inbox,
)

registry.register(
    {
        "name": "email_search", "description": "Search emails by subject keyword.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "limit": {"type": "integer"},
        }, "required": ["query"]},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "emails": {"type": "array"}}},
        "scopes": ["email:read"], "tags": ["productivity", "email"],
    }, _email_search,
)

registry.register(
    {
        "name": "email_read", "description": "Read the full content of an email by its UID.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"uid": {"type": "string"}}, "required": ["uid"]},
        "returns": {"type": "object", "properties": {"subject": {"type": "string"}, "body": {"type": "string"}}},
        "scopes": ["email:read"], "tags": ["productivity", "email"],
    }, _email_read,
)

registry.register(
    {
        "name": "email_send", "description": "Send an email to a recipient.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_always", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"},
        }, "required": ["to", "subject", "body"]},
        "returns": {"type": "object", "properties": {"sent": {"type": "boolean"}}},
        "scopes": ["email:write"], "tags": ["productivity", "email"],
    }, _email_send,
)
