import pytest
from datetime import datetime, timedelta, UTC
from backend.plugins.reminders import _set_reminder, _list_reminders, _cancel_reminder, _plan_today, _connection

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    """Use a temporary database for testing."""
    test_db = tmp_path / "test_brain.db"
    monkeypatch.setattr("backend.plugins.reminders.DB_PATH", test_db)
    
    # Initialize the table
    with _connection():
        pass
    
    yield test_db

def test_reminder_set():
    due = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    reminder = _set_reminder("Buy milk", due, "Whole milk")
    
    assert reminder["title"] == "Buy milk"
    assert reminder["notes"] == "Whole milk"
    assert "id" in reminder
    assert "due_at" in reminder
    assert "created_at" in reminder

def test_reminder_set_invalid_date():
    with pytest.raises(ValueError, match="due_at must be an ISO-8601 date/time"):
        _set_reminder("Buy milk", "tomorrow")

def test_reminder_list():
    due = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    _set_reminder("Reminder 1", due)
    _set_reminder("Reminder 2", due)
    
    result = _list_reminders()
    assert result["count"] == 2
    assert result["reminders"][0]["title"] == "Reminder 1"
    assert result["reminders"][1]["title"] == "Reminder 2"

def test_reminder_cancel():
    due = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    rem = _set_reminder("Cancel me", due)
    rem_id = rem["id"]
    
    # Cancel it
    res = _cancel_reminder(rem_id)
    assert res["cancelled"] is True
    assert res["already_cancelled"] is False
    
    # Try to cancel again
    res2 = _cancel_reminder(rem_id)
    assert res2["cancelled"] is True
    assert res2["already_cancelled"] is True
    
    # Ensure it's hidden from the active list
    result = _list_reminders(include_cancelled=False)
    assert result["count"] == 0
    
    # Ensure it's in the complete list
    result_all = _list_reminders(include_cancelled=True)
    assert result_all["count"] == 1
    assert result_all["reminders"][0]["cancelled_at"] is not None

def test_plan_today(monkeypatch):
    # Mock memories
    monkeypatch.setattr("backend.plugins.reminders.list_memories", lambda: [])
    
    now = datetime.now(UTC)
    # Reminder due today
    due_today = (now + timedelta(hours=1)).isoformat()
    _set_reminder("Today reminder", due_today)
    
    # Reminder due tomorrow
    due_tomorrow = (now + timedelta(days=1)).isoformat()
    _set_reminder("Tomorrow reminder", due_tomorrow)
    
    result = _plan_today(now.date().isoformat())
    assert result["count"] == 1
    assert result["ordered_plan"][0]["title"] == "Today reminder"
