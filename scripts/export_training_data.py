#!/usr/bin/env python3
"""
Export interaction logs and tool executions from SQLite to standard JSONL format
for LoRA / QLoRA fine-tuning (Unsloth / Hugging Face / Ollama).
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "backend" / "data" / "jarvis.db"
OUTPUT_PATH = ROOT / "backend" / "data" / "training_dataset.jsonl"

SYSTEM_PROMPT = (
    "You are Jarvis: a close personal assistant that knows the user, "
    "executes real actions via tools, and communicates concisely with precision."
)

def export_training_data(db_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    samples = []
    
    # Check if database exists
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check interaction_log table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interaction_log'")
            if cursor.fetchone():
                cursor.execute("SELECT topic, intent, context_json FROM interaction_log ORDER BY id ASC")
                for row in cursor.fetchall():
                    topic, intent, context_json = row
                    user_msg = f"Intent: {intent}" if intent else (topic or "Status check")
                    assistant_msg = f"Acknowledged. Executing {intent or 'routine task'}."
                    
                    samples.append({
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                            {"role": "assistant", "content": assistant_msg}
                        ]
                    })
            conn.close()
        except Exception as exc:
            print(f"[WARN] Error querying local DB: {exc}")

    # Seed default bootstrap dataset if DB has few entries
    if len(samples) < 5:
        bootstrap_data = [
            ("What is your current system status?", "All systems operational. Brain is connected, tools are active, and presence clients are synced."),
            ("Remind me to check server logs at 6 PM.", "Reminder set for 6:00 PM: Check server logs."),
            ("Switch to focus mode.", "Focus mode activated. Muting non-essential background notifications."),
            ("Run system diagnostics.", "Running diagnostic suite across local database, tool registry, and WebSocket bridge."),
            ("Summarize today's activities.", "Today's summary: 3 background tasks executed, documentation synced, and all integrity tests passed.")
        ]
        for user_text, assist_text in bootstrap_data:
            samples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": assist_text}
                ]
            })

    with open(output_path, "w", encoding="utf-8") as f:
        for item in samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[OK] Exported {len(samples)} training samples to {output_path.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    sys.exit(export_training_data(DB_PATH, OUTPUT_PATH))
