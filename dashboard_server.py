"""Production Live Web Dashboard Server for Jarvis Client Radar.

Full-Stack Self-Contained Local Web Server:
- Real REST API endpoints backed by SQLite (`leads_ledger.db`).
- Live Inbound Feed Scanner trigger.
- Live YouTube Creator Outbound Radar search.
- Live Funnel Analytics & Status updates (SENT, REPLIED, WON).
- 100% Offline-Resilient UI (Embedded styles & JavaScript, zero CDN dependency failures).
"""

import os
import json
import sqlite3
import asyncio
import urllib.parse
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webbrowser
import httpx

ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT_DIR / "leads_ledger.db"

app = FastAPI(title="Jarvis Client Radar HUD")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT,
                niche TEXT,
                pitch TEXT,
                is_high_value INTEGER DEFAULT 0,
                loom_audit_notes TEXT,
                status TEXT DEFAULT 'SENT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# --- API Endpoints ---

@app.get("/api/stats")
async def get_stats():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM leads WHERE is_high_value = 1")
        high_val = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
        status_counts = dict(cursor.fetchall())
        
        cursor.execute("SELECT niche, COUNT(*) FROM leads GROUP BY niche")
        niche_counts = [dict(row) for row in cursor.fetchall()]
        
    return {
        "total": total,
        "high_val": high_val,
        "sent": status_counts.get("SENT", 0),
        "replied": status_counts.get("REPLIED", 0),
        "won": status_counts.get("WON", 0),
        "niches": niche_counts
    }

@app.get("/api/leads")
async def get_leads():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50")
        rows = [dict(row) for row in cursor.fetchall()]
    return {"leads": rows}

@app.post("/api/status")
async def update_status(payload: dict):
    lead_id = payload.get("id")
    new_status = payload.get("status", "SENT").upper()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
        conn.commit()
    return {"success": True, "id": lead_id, "status": new_status}

@app.post("/api/scan")
async def trigger_scan():
    """Triggers the real inbound feed scanner."""
    try:
        from freelance_lead_triage import run_master_triage_engine
        await run_master_triage_engine()
        return {"success": True, "message": "Inbound scan completed successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/audit-creator")
async def audit_creator(payload: dict):
    """Audits YouTube creator by query or channel."""
    query = payload.get("query", "finance podcast india")
    try:
        from youtube_creator_auditor import discover_creator_channels_by_keyword, fetch_channel_recent_videos, generate_cold_creator_audit, FALLBACK_CHANNELS
        async with httpx.AsyncClient() as client:
            channels = await discover_creator_channels_by_keyword(client, query)
            if not channels:
                channels = FALLBACK_CHANNELS
            
            target = channels[0]
            videos = await fetch_channel_recent_videos(client, target["channel_id"])
            if videos:
                name = videos[0].get("channel_name", target["name"])
                pitch = await generate_cold_creator_audit(name, videos)
                return {
                    "success": True,
                    "creator_name": name,
                    "latest_video": videos[0]["title"],
                    "video_link": videos[0]["link"],
                    "audit_pitch": pitch
                }
        return {"success": False, "error": "No videos found for this niche query."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/followup/{lead_id}")
async def get_followup(lead_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "Lead not found"}
        
        return {
            "success": True,
            "title": row["title"],
            "pitch": (
                f"Awesome! Here is a sample of my recent work: https://youtube.com/@your_editing_reel\n\n"
                f"To keep everything smooth and predictable, I usually work on a fixed monthly retainer:\n\n"
                f"📦 THE CREATOR RETENTION PACKAGE (₹14,999/mo or $499/mo):\n"
                f"• 8 High-Retention Reels / Shorts / TikToks (Hooks, Kinetic Captions, Sound Design)\n"
                f"• 4 High-CTR YouTube Thumbnails\n"
                f"• 48-Hour Turnaround + Unlimited Revisions\n"
                f"• Zero Hourly Tracking Friction\n\n"
                f"If you'd like to test the waters, I can do your first video as a trial cut today. What does your schedule look like for a quick kickoff?"
            )
        }

# --- Embedded Full-Featured Dashboard Web Page ---
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis Client Acquisition HUD (v5.0)</title>
    <style>
        :root {
            --bg: #090a0f;
            --card-bg: #12141c;
            --border: #232738;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.25);
            --text: #f3f4f6;
            --muted: #9ca3af;
            --success: #10b981;
            --warning: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; padding-bottom: 40px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 18px 32px; background: rgba(18, 20, 28, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
        .header-title { font-size: 20px; font-weight: 700; background: linear-gradient(90deg, #60a5fa, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .badge { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .btn { background: var(--accent); color: #fff; border: none; padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 0 16px var(--accent-glow); display: inline-flex; align-items: center; gap: 8px; }
        .btn:hover { background: #2563eb; transform: translateY(-1px); }
        .btn-secondary { background: rgba(255, 255, 255, 0.08); color: var(--text); box-shadow: none; border: 1px solid var(--border); }
        .btn-secondary:hover { background: rgba(255, 255, 255, 0.15); }
        .container { max-width: 1280px; margin: 28px auto; padding: 0 24px; }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 32px; }
        .stat-card { background: var(--card-bg); border: 1px solid var(--border); padding: 20px; border-radius: 16px; transition: border-color 0.2s; }
        .stat-card:hover { border-color: var(--accent); }
        .stat-label { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-val { font-size: 32px; font-weight: 800; margin: 8px 0; }
        .main-layout { display: grid; grid-template-columns: 7fr 5fr; gap: 24px; }
        @media (max-width: 960px) { .main-layout { grid-template-columns: 1fr; } }
        .panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 18px; padding: 24px; }
        .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
        .panel-title { font-size: 17px; font-weight: 700; }
        .lead-card { background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 14px; padding: 18px; margin-bottom: 16px; transition: border-color 0.2s; }
        .lead-card:hover { border-color: rgba(96, 165, 250, 0.4); }
        .lead-title { font-size: 15px; font-weight: 600; color: #fff; margin-bottom: 8px; }
        .lead-meta { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }
        .tag { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 6px; }
        .tag-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
        .tag-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
        .tag-green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
        .pitch-box { background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.06); padding: 14px; border-radius: 10px; font-size: 13px; line-height: 1.5; color: #d1d5db; margin-bottom: 14px; }
        .actions-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
        .search-bar { display: flex; gap: 8px; margin-bottom: 18px; }
        .search-input { flex: 1; background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border); padding: 10px 14px; border-radius: 10px; color: #fff; font-size: 14px; }
        .search-input:focus { outline: none; border-color: var(--accent); }
        .creator-result { background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-top: 14px; }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(8px); z-index: 200; align-items: center; justify-content: center; }
        .modal-content { background: var(--card-bg); border: 1px solid var(--border); width: 90%; max-width: 600px; padding: 24px; border-radius: 18px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
    </style>
</head>
<body>
    <header class="header">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;"></div>
            <div class="header-title">JARVIS CLIENT RADAR HUD</div>
            <span class="badge">Live Server (Port 5050)</span>
        </div>
        <button class="btn" onclick="triggerScan()">
            <span id="scan-btn-text">⚡ Run Live Inbound Scan</span>
        </button>
    </header>

    <div class="container">
        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Total Leads Logged</div>
                <div class="stat-val" id="stat-total">0</div>
                <div style="font-size: 12px; color: var(--success);">● Auto Deduplicated</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High-Value Gigs ($1k+)</div>
                <div class="stat-val" style="color: var(--warning);" id="stat-high-val">0</div>
                <div style="font-size: 12px; color: var(--muted);">Loom Audit Triggers</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Client Replies</div>
                <div class="stat-val" style="color: var(--accent);" id="stat-replied">0</div>
                <div style="font-size: 12px; color: var(--muted);">Permission Granted</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Gigs Won / Closed</div>
                <div class="stat-val" style="color: var(--success);" id="stat-won">0</div>
                <div style="font-size: 12px; color: var(--muted);">₹14,999/mo Retainers</div>
            </div>
        </div>

        <div class="main-layout">
            <!-- Left: Live Inbound Leads -->
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">🔥 Inbound Lead Triage Feed</div>
                    <span id="lead-count-badge" class="badge">0 Leads</span>
                </div>
                <div id="leads-list">
                    <div style="color: var(--muted); text-align: center; padding: 30px;">Loading leads from SQLite...</div>
                </div>
            </div>

            <!-- Right: Cold YouTube Creator Radar -->
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">🎯 Creator Outbound Radar</div>
                    <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.3);">0 Competition</span>
                </div>
                <div class="search-bar">
                    <input type="text" id="creator-query" class="search-input" placeholder="e.g. finance podcast india, saas demo">
                    <button class="btn" onclick="auditCreator()">Audit</button>
                </div>
                <div id="creator-output" style="display: none;" class="creator-result">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div>
                            <h4 id="creator-name" style="font-size: 15px; font-weight: 700; color: #fff;">Creator Name</h4>
                            <p id="creator-video" style="font-size: 12px; color: var(--muted); margin-top: 2px;">Latest: ...</p>
                        </div>
                        <span class="tag tag-green">Verified</span>
                    </div>
                    <div id="creator-pitch" class="pitch-box">...</div>
                    <button class="btn btn-secondary" style="width: 100%; justify-content: center;" onclick="copyText('creator-pitch')">📋 Copy Cold Value Pitch</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Upsell Modal -->
    <div id="upsell-modal" class="modal">
        <div class="modal-content">
            <h3 style="font-size: 18px; margin-bottom: 12px; color: #fff;">📦 Productized Retainer Package Pitch</h3>
            <div id="modal-pitch-body" class="pitch-box" style="white-space: pre-wrap; font-size: 13px; max-height: 300px; overflow-y: auto;"></div>
            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px;">
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                <button class="btn" onclick="copyModalPitch()">📋 Copy Pitch</button>
            </div>
        </div>
    </div>

    <script>
        async function fetchStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('stat-total').innerText = data.total;
                document.getElementById('stat-high-val').innerText = data.high_val;
                document.getElementById('stat-replied').innerText = data.replied;
                document.getElementById('stat-won').innerText = data.won;
                document.getElementById('lead-count-badge').innerText = `${data.total} Leads`;
            } catch (e) {
                console.error("Failed to load stats", e);
            }
        }

        async function fetchLeeds() {
            try {
                const res = await fetch('/api/leads');
                const data = await res.json();
                const container = document.getElementById('leads-list');
                
                if (data.leads.length === 0) {
                    container.innerHTML = '<div style="color: var(--muted); text-align: center; padding: 40px;">No leads found. Click "Run Live Inbound Scan" above to fetch latest gigs!</div>';
                    return;
                }

                container.innerHTML = data.leads.map(lead => `
                    <div class="lead-card">
                        <div class="lead-meta">
                            <span class="tag tag-blue">${lead.niche ? lead.niche.toUpperCase() : 'GENERAL'}</span>
                            ${lead.is_high_value ? '<span class="tag tag-amber">👑 HIGH VALUE ($1k+)</span>' : ''}
                            <span class="tag ${lead.status === 'WON' ? 'tag-green' : lead.status === 'REPLIED' ? 'tag-blue' : 'tag-secondary'}">${lead.status}</span>
                        </div>
                        <div class="lead-title">${lead.title}</div>
                        <div class="pitch-box" id="pitch-${lead.id}">${lead.pitch}</div>
                        ${lead.loom_audit_notes ? `<div style="font-size: 12px; color: #fbbf24; margin-bottom: 10px;">📹 <b>Loom Script:</b> ${lead.loom_audit_notes}</div>` : ''}
                        <div class="actions-row">
                            <div style="display: flex; gap: 8px;">
                                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="copyElementText('pitch-${lead.id}')">📋 Copy</button>
                                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="openFollowupModal('${lead.id}')">📦 Retainer Offer</button>
                                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px; color: #34d399;" onclick="setStatus('${lead.id}', 'WON')">✅ Won</button>
                            </div>
                            <a href="${lead.link}" target="_blank" class="btn" style="padding: 6px 14px; font-size: 12px;">🚀 Open Post</a>
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                console.error("Failed to load leads", e);
            }
        }

        async function triggerScan() {
            const btnText = document.getElementById('scan-btn-text');
            btnText.innerText = '⏳ Scanning Feeds...';
            try {
                const res = await fetch('/api/scan', { method: 'POST' });
                const data = await res.json();
                btnText.innerText = '✅ Scan Complete!';
                await fetchStats();
                await fetchLeeds();
                setTimeout(() => { btnText.innerText = '⚡ Run Live Inbound Scan'; }, 2000);
            } catch (e) {
                btnText.innerText = '❌ Scan Failed';
            }
        }

        async function auditCreator() {
            const query = document.getElementById('creator-query').value || 'finance podcast india';
            const output = document.getElementById('creator-output');
            output.style.display = 'block';
            document.getElementById('creator-name').innerText = 'Auditing YouTube channels...';
            document.getElementById('creator-pitch').innerText = 'Extracting recent video hooks and crafting value audit...';
            
            try {
                const res = await fetch('/api/audit-creator', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await res.json();
                if (data.success) {
                    document.getElementById('creator-name').innerText = data.creator_name;
                    document.getElementById('creator-video').innerText = `Latest: "${data.latest_video}"`;
                    document.getElementById('creator-pitch').innerText = data.audit_pitch;
                } else {
                    document.getElementById('creator-pitch').innerText = data.error || 'No channels found.';
                }
            } catch (e) {
                document.getElementById('creator-pitch').innerText = 'Failed to run creator audit.';
            }
        }

        async function openFollowupModal(leadId) {
            const res = await fetch(`/api/followup/${leadId}`);
            const data = await res.json();
            if (data.success) {
                document.getElementById('modal-pitch-body').innerText = data.pitch;
                document.getElementById('upsell-modal').style.display = 'flex';
            }
        }

        async function setStatus(leadId, status) {
            await fetch('/api/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: leadId, status: status })
            });
            fetchStats();
            fetchLeeds();
        }

        function closeModal() {
            document.getElementById('upsell-modal').style.display = 'none';
        }

        function copyElementText(elemId) {
            const text = document.getElementById(elemId).innerText;
            navigator.clipboard.writeText(text);
            alert('Copied pitch to clipboard!');
        }

        function copyText(elemId) {
            const text = document.getElementById(elemId).innerText;
            navigator.clipboard.writeText(text);
            alert('Copied creator pitch to clipboard!');
        }

        function copyModalPitch() {
            const text = document.getElementById('modal-pitch-body').innerText;
            navigator.clipboard.writeText(text);
            alert('Copied productized retainer pitch!');
            closeModal();
        }

        // Auto load on start
        fetchStats();
        fetchLeeds();
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

def start_server():
    print("=" * 60)
    print("[*] STARTING LIVE JARVIS DASHBOARD HUD (http://localhost:5050)")
    print("=" * 60)
    webbrowser.open("http://localhost:5050")
    uvicorn.run(app, host="127.0.0.1", port=5050, log_level="info")

if __name__ == "__main__":
    start_server()
