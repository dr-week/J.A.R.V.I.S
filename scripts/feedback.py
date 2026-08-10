#!/usr/bin/env python3
"""Jarvis Feedback Dashboard.

A live rich terminal UI (Textual) that monitors:
- The devloop board status
- The active memory and habit stores in the brain
- The brain's health and connection status

Usage:
    python scripts/feedback.py
"""
import os
import subprocess
import sys

try:
    import httpx
    from textual import work
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Grid, Vertical
    from textual.widgets import DataTable, Footer, Header, Label, Static
except ImportError:
    print("Missing dependencies. Please run:")
    print("pip install textual httpx")
    sys.exit(1)

class FeedbackDashboard(App):
    CSS = """
    Screen {
        background: #0d0d14;
    }
    
    Grid {
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 1;
    }
    
    .panel {
        border: solid #4c1d95;
        padding: 1;
        background: #1a1a2e;
        height: 100%;
        margin-right: 1;
    }
    
    .panel-title {
        color: #a78bfa;
        text-style: bold;
        margin-bottom: 1;
        border-bottom: solid #4c1d95;
    }
    
    DataTable {
        height: 1fr;
        margin-bottom: 1;
        border: solid #2d2d44;
    }
    
    #brain-status {
        color: #10b981;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_all", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Grid():
            # Left column: Board
            with Vertical(classes="panel"):
                yield Label("📋 DEVLOOP BOARD", classes="panel-title")
                yield Static(id="board-status", markup=False)
                
            # Right column: Habits, Memories, and System
            with Vertical(classes="panel"):
                yield Label("🧠 SOUL & BRAIN (Live)", classes="panel-title")
                
                with Horizontal():
                    with Vertical():
                        yield Label("[bold]Memories[/bold]")
                        yield DataTable(id="memories-table")
                    with Vertical():
                        yield Label("[bold]Habits[/bold]")
                        yield DataTable(id="habits-table")
                        
                yield Label("[bold]Sessions[/bold]")
                yield DataTable(id="sessions-table", classes="small-table")
                
                yield Label("[bold]Brain System Status[/bold]")
                yield Static(id="brain-status", markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Jarvis Dev Feedback Loop"
        
        # Setup tables
        memories = self.query_one("#memories-table", DataTable)
        memories.add_columns("Key", "Value", "Source")
        
        habits = self.query_one("#habits-table", DataTable)
        habits.add_columns("Type", "Key", "Value", "Confidence")
        
        sessions = self.query_one("#sessions-table", DataTable)
        sessions.add_columns("Session ID", "Device ID", "Updated At", "Title")

        self.refresh_all()
        # Auto-refresh every 5 seconds
        self.set_interval(5, self.refresh_all)

    @work
    async def refresh_all(self):
        # 1. Update Board Status (local command)
        try:
            # Run the same python executable being used for the script
            result = subprocess.run(
                [sys.executable, "scripts/devloop.py", "status"], 
                capture_output=True, 
                text=True
            )
            self.query_one("#board-status", Static).update(result.stdout)
        except Exception as e:
            self.query_one("#board-status", Static).update(f"Error reading board: {e}")

        # 2. Update Brain Info (API calls)
        try:
            async with httpx.AsyncClient(base_url="http://localhost:8787", timeout=2) as client:
                # Health
                r = await client.get("/health")
                r.raise_for_status()
                h = r.json()
                
                # Also hit sync status
                sr = await client.get("/sync/status")
                sync_clients = sr.json().get("connected_clients", 0) if sr.status_code == 200 else 0
                
                status_text = (
                    f"Name: [bold]{h.get('assistant_name')}[/bold] | "
                    f"LLM: {h.get('llm_provider')} | "
                    f"Ready: {h.get('llm_ready')} | "
                    f"Learning: {'[green]ON[/green]' if h.get('learning_enabled') else '[red]OFF[/red]'} | "
                    f"WS Clients: {sync_clients}"
                )
                self.query_one("#brain-status", Static).update(status_text)
                
                # Memories
                r = await client.get("/soul/memories")
                m_table = self.query_one("#memories-table", DataTable)
                m_table.clear()
                for m in r.json().get("memories", []):
                    m_table.add_row(m.get("key"), m.get("value"), m.get("source"))
                    
                # Habits
                r = await client.get("/soul/habits")
                h_table = self.query_one("#habits-table", DataTable)
                h_table.clear()
                for h_item in r.json().get("habits", []):
                    h_table.add_row(
                        h_item.get("pattern_type"), 
                        h_item.get("pattern_key"), 
                        h_item.get("pattern_value"), 
                        f"{h_item.get('confidence', 0):.2f}"
                    )
                    
                # Try fetching sessions by reading local SQLite DB since it's a devtool
                try:
                    import sqlite3
                    # Fallback to local DB for sessions since no API endpoint exists yet
                    db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "brain.db")
                    if os.path.exists(db_path):
                        with sqlite3.connect(db_path) as conn:
                            conn.row_factory = sqlite3.Row
                            rows = conn.execute("SELECT id, device_id, updated_at, title FROM sessions ORDER BY updated_at DESC LIMIT 10").fetchall()
                            s_table = self.query_one("#sessions-table", DataTable)
                            s_table.clear()
                            for r in rows:
                                s_table.add_row(r["id"], r["device_id"], r["updated_at"], r["title"])
                except Exception as db_e:
                    self.query_one("#board-status", Static).update(f"DB Error: {db_e}")
        except Exception as e:
            self.query_one("#brain-status", Static).update(f"[red]Brain unreachable: {e}[/red]")

if __name__ == "__main__":
    app = FeedbackDashboard()
    app.run()
