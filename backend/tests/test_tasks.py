import sqlite3
import pytest
from backend.plugins.tasks import _task_add, _task_list, _task_complete, _connection

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    """Use a temporary database for testing."""
    test_db = tmp_path / "test_brain.db"
    monkeypatch.setattr("backend.plugins.tasks.DB_PATH", test_db)
    
    # Initialize the table
    with _connection():
        pass
    
    yield test_db

def test_task_add():
    task = _task_add("Buy groceries", "Milk, eggs, bread")
    assert task["title"] == "Buy groceries"
    assert task["description"] == "Milk, eggs, bread"
    assert "id" in task
    assert "created_at" in task

def test_task_add_empty_title():
    with pytest.raises(ValueError, match="title cannot be empty"):
        _task_add("   ")

def test_task_list():
    _task_add("Task 1")
    _task_add("Task 2")
    
    result = _task_list()
    assert result["count"] == 2
    assert result["tasks"][0]["title"] == "Task 1"
    assert result["tasks"][1]["title"] == "Task 2"

def test_task_complete():
    task = _task_add("Complete me")
    task_id = task["id"]
    
    # Complete it
    res = _task_complete(task_id)
    assert res["completed"] is True
    assert res["already_completed"] is False
    
    # Try to complete it again
    res2 = _task_complete(task_id)
    assert res2["completed"] is True
    assert res2["already_completed"] is True
    
    # Ensure it's hidden from the active list
    result = _task_list(include_completed=False)
    assert result["count"] == 0
    
    # Ensure it's in the complete list
    result_all = _task_list(include_completed=True)
    assert result_all["count"] == 1
    assert result_all["tasks"][0]["completed_at"] is not None

def test_task_complete_invalid_id():
    with pytest.raises(ValueError, match="No task found with id"):
        _task_complete("invalid-id")
