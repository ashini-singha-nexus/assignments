"""
Advanced tests for JSON-backed TODO system with tags and due dates.

This module contains comprehensive tests for the todo_core functionality,
covering CRUD operations, filtering, sorting, and validation.
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, date, timedelta
from pathlib import Path

from assignments.todo_core import (
    add_task, list_tasks, complete_task, update_task, delete_task,
    _validate_date, _validate_tags, _is_past_due
)

# Test data
TEST_TASKS = [
    {
        "id": 1,
        "title": "Write tests",
        "done": False,
        "tags": ["dev", "qa"],
        "due": "2025-09-05",
        "created_at": "2025-08-20T10:00:00.000000"
    },
    {
        "id": 2,
        "title": "Refactor core",
        "done": False,
        "tags": ["backend"],
        "due": "2025-09-10",
        "created_at": "2025-08-19T10:00:00.000000"
    },
    {
        "id": 3,
        "title": "Update documentation",
        "done": True,
        "tags": ["docs"],
        "due": None,
        "created_at": "2025-08-18T10:00:00.000000"
    }
]

@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    
    # Initialize with test data
    with open(path, 'w') as f:
        json.dump(TEST_TASKS, f, indent=2)
    
    yield path
    
    # Clean up
    os.unlink(path)

def test_add_task(temp_db):
    """Test adding a new task."""
    # Add a new task
    new_task = add_task(temp_db, "New test task", tags=["test"], due="2025-10-01")
    
    # Verify the task was added with correct data
    assert new_task["title"] == "New test task"
    assert new_task["tags"] == ["test"]
    assert new_task["due"] == "2025-10-01"
    assert new_task["done"] is False
    assert "created_at" in new_task
    
    # Verify the task was saved to the database
    tasks = list_tasks(temp_db)
    assert len(tasks) == 4  # 3 initial + 1 new
    assert any(task["title"] == "New test task" for task in tasks)

def test_add_task_validation(temp_db):
    """Test validation when adding tasks."""
    # Test empty title
    with pytest.raises(ValueError, match="Title cannot be empty"):
        add_task(temp_db, "")
    
    # Test invalid date format
    with pytest.raises(ValueError, match="Invalid date format"):
        add_task(temp_db, "Test task", due="2025/09/01")
    
    # Test tags validation
    task = add_task(temp_db, "Test task", tags="tag1,tag2")
    assert task["tags"] == ["tag1", "tag2"]
    
    task = add_task(temp_db, "Test task", tags=["tag1", "tag2"])
    assert task["tags"] == ["tag1", "tag2"]

def test_list_tasks_filtering(temp_db):
    """Test filtering tasks."""
    # Filter by status
    open_tasks = list_tasks(temp_db, status="open")
    assert len(open_tasks) == 2
    assert all(not task["done"] for task in open_tasks)
    
    done_tasks = list_tasks(temp_db, status="done")
    assert len(done_tasks) == 1
    assert all(task["done"] for task in done_tasks)
    
    # Filter by tags
    dev_tasks = list_tasks(temp_db, tags=["dev"])
    assert len(dev_tasks) == 1
    assert "dev" in dev_tasks[0]["tags"]
    
    # Filter by due date
    due_before_tasks = list_tasks(temp_db, due_before="2025-09-06")
    assert len(due_before_tasks) == 1
    assert due_before_tasks[0]["due"] == "2025-09-05"

def test_list_tasks_sorting(temp_db):
    """Test sorting tasks."""
    # Sort by due date (tasks without due come last)
    sorted_by_due = list_tasks(temp_db, sort_by="due")
    assert sorted_by_due[0]["due"] == "2025-09-05"
    assert sorted_by_due[1]["due"] == "2025-09-10"
    assert sorted_by_due[2]["due"] is None
    
    # Sort by title
    sorted_by_title = list_tasks(temp_db, sort_by="title")
    titles = [task["title"] for task in sorted_by_title]
    assert titles == ["Refactor core", "Update documentation", "Write tests"]
    
    # Sort by created (oldest first)
    sorted_by_created = list_tasks(temp_db, sort_by="created")
    created_dates = [task["created_at"] for task in sorted_by_created]
    assert created_dates == [
        "2025-08-18T10:00:00.000000",
        "2025-08-19T10:00:00.000000", 
        "2025-08-20T10:00:00.000000"
    ]

def test_complete_task(temp_db):
    """Test completing a task."""
    # Complete a task
    result = complete_task(temp_db, 1)
    assert result is True
    
    # Verify the task is marked as done
    tasks = list_tasks(temp_db)
    task_1 = next(task for task in tasks if task["id"] == 1)
    assert task_1["done"] is True
    
    # Try to complete a non-existent task
    result = complete_task(temp_db, 999)
    assert result is False

def test_update_task(temp_db):
    """Test updating a task."""
    # Update task fields
    result = update_task(temp_db, 1, title="Updated title", tags=["new_tag"], due="2025-12-01")
    assert result is True
    
    # Verify the updates
    tasks = list_tasks(temp_db)
    task_1 = next(task for task in tasks if task["id"] == 1)
    assert task_1["title"] == "Updated title"
    assert task_1["tags"] == ["new_tag"]
    assert task_1["due"] == "2025-12-01"
    
    # Try to update a non-existent task
    result = update_task(temp_db, 999, title="New title")
    assert result is False
    
    # Test validation during update
    with pytest.raises(ValueError, match="Title cannot be empty"):
        update_task(temp_db, 1, title="")

def test_delete_task(temp_db):
    """Test deleting a task."""
    # Delete a task
    result = delete_task(temp_db, 1)
    assert result is True
    
    # Verify the task is deleted
    tasks = list_tasks(temp_db)
    assert len(tasks) == 2
    assert all(task["id"] != 1 for task in tasks)
    
    # Try to delete a non-existent task
    result = delete_task(temp_db, 999)
    assert result is False

def test_validate_date():
    """Test date validation."""
    # Valid dates
    assert _validate_date("2025-09-01") == "2025-09-01"
    assert _validate_date(None) is None
    
    # Invalid dates
    with pytest.raises(ValueError, match="Invalid date format"):
        _validate_date("2025/09/01")
    
    with pytest.raises(ValueError, match="Invalid date format"):
        _validate_date("not-a-date")

def test_validate_tags():
    """Test tags validation."""
    # Valid tags formats
    assert _validate_tags("tag1,tag2") == ["tag1", "tag2"]
    assert _validate_tags(["tag1", "tag2"]) == ["tag1", "tag2"]
    assert _validate_tags(None) == []
    
    # Empty tags are filtered out
    assert _validate_tags("tag1,,tag2") == ["tag1", "tag2"]
    
    # Invalid tags format
    with pytest.raises(ValueError, match="Tags must be a list of strings"):
        _validate_tags(123)

def test_is_past_due():
    """Test past due date detection."""
    # Past due date
    past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    assert _is_past_due(past_date) is True
    
    # Future due date
    future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert _is_past_due(future_date) is False
    
    # No due date
    assert _is_past_due(None) is False
    
    # Invalid date format
    assert _is_past_due("invalid-date") is False

def test_empty_database():
    """Test operations with an empty database."""
    # Create a temporary empty database
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    
    try:
        # Add a task to empty database
        task = add_task(path, "First task")
        assert task["id"] == 1
        
        # List tasks
        tasks = list_tasks(path)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "First task"
        
        # Complete task
        result = complete_task(path, 1)
        assert result is True
        
        # Update task
        result = update_task(path, 1, title="Updated task")
        assert result is True
        
        # Delete task
        result = delete_task(path, 1)
        assert result is True
        
        # Verify database is empty again
        tasks = list_tasks(path)
        assert len(tasks) == 0
        
    finally:
        os.unlink(path)

def test_stable_sorting(temp_db):
    """Test that sorting is stable (ties broken by ID)."""
    # Add tasks with the same due date
    add_task(temp_db, "Task A", due="2025-09-05")
    add_task(temp_db, "Task B", due="2025-09-05")
    
    # Sort by due date - should maintain insertion order for same due dates
    tasks = list_tasks(temp_db, sort_by="due")
    
    # Find our test tasks
    task_a = next(task for task in tasks if task["title"] == "Task A")
    task_b = next(task for task in tasks if task["title"] == "Task B")
    
    # Task A should come before Task B due to stable sorting
    assert tasks.index(task_a) < tasks.index(task_b)