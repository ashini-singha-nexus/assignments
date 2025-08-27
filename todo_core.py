"""
Core functionality for JSON-backed TODO system with tags and due dates.

This module provides functions for managing TODO tasks stored in a JSON file.
Each task has an ID, title, completion status, tags, due date, and creation timestamp.
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Task schema:
# {
#   "id": int,
#   "title": str,
#   "done": bool,
#   "tags": List[str],
#   "due": "YYYY-MM-DD" or None,
#   "created_at": "ISO8601"
# }

def _read_tasks(path: str) -> List[Dict[str, Any]]:
    """
    Read tasks from JSON file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        List of task dictionaries
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write_tasks(path: str, tasks: List[Dict[str, Any]]) -> None:
    """
    Write tasks to JSON file.
    
    Args:
        path: Path to the JSON file
        tasks: List of task dictionaries to write
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2)

def _validate_date(date_str: Optional[str]) -> Optional[str]:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Validated date string or None
        
    Raises:
        ValueError: If date format is invalid
    """
    if date_str is None:
        return None
        
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

def _validate_tags(tags: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Validate and normalize tags.
    
    Args:
        tags: Tags as string (comma-separated) or list
        
    Returns:
        List of normalized tags
        
    Raises:
        ValueError: If tags format is invalid
    """
    if tags is None:
        return []
        
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]
    
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("Tags must be a list of strings or comma-separated string")
    
    # Remove empty tags and duplicates
    tags = [tag for tag in tags if tag]
    return list(set(tags))

def _is_past_due(due_date: Optional[str]) -> bool:
    """
    Check if a due date is in the past.
    
    Args:
        due_date: Due date string in YYYY-MM-DD format or None
        
    Returns:
        True if the due date is in the past, False otherwise
    """
    if due_date is None:
        return False
        
    try:
        due = datetime.strptime(due_date, '%Y-%m-%d').date()
        return due < date.today()
    except ValueError:
        return False

def add_task(path: str, title: str, tags: Optional[Union[str, List[str]]] = None, 
             due: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new task to the TODO list.
    
    Args:
        path: Path to the JSON file
        title: Title of the task
        tags: Optional tags as comma-separated string or list
        due: Optional due date in YYYY-MM-DD format
        
    Returns:
        The created task dictionary
        
    Raises:
        ValueError: If title is empty or date format is invalid
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    # Validate inputs
    validated_due = _validate_date(due)
    validated_tags = _validate_tags(tags)
    
    # Read existing tasks
    tasks = _read_tasks(path)
    
    # Generate new ID
    if tasks:
        new_id = max(task['id'] for task in tasks) + 1
    else:
        new_id = 1
    
    # Create new task
    new_task = {
        'id': new_id,
        'title': title.strip(),
        'done': False,
        'tags': validated_tags,
        'due': validated_due,
        'created_at': datetime.now().isoformat()
    }
    
    # Add to list and save
    tasks.append(new_task)
    _write_tasks(path, tasks)
    
    return new_task

def list_tasks(path: str, status: Optional[str] = None, tags: Optional[List[str]] = None,
               due_before: Optional[str] = None, sort_by: str = "due") -> List[Dict[str, Any]]:
    """
    List tasks with optional filtering and sorting.
    
    Args:
        path: Path to the JSON file
        status: Filter by status - "open", "done", or None for all
        tags: Filter by tags (list of tags)
        due_before: Filter by due date before this date (YYYY-MM-DD)
        sort_by: Sort by "due", "created", or "title"
        
    Returns:
        List of filtered and sorted task dictionaries
        
    Raises:
        ValueError: If status or sort_by values are invalid
    """
    # Validate inputs
    if status not in (None, "open", "done"):
        raise ValueError('Status must be None, "open", or "done"')
    
    if sort_by not in ("due", "created", "title"):
        raise ValueError('sort_by must be "due", "created", or "title"')
    
    validated_due_before = _validate_date(due_before) if due_before else None
    
    # Read tasks
    tasks = _read_tasks(path)
    
    # Apply filters
    filtered_tasks = tasks
    
    if status == "open":
        filtered_tasks = [task for task in filtered_tasks if not task['done']]
    elif status == "done":
        filtered_tasks = [task for task in filtered_tasks if task['done']]
    
    if tags:
        filtered_tasks = [task for task in filtered_tasks 
                         if any(tag in task['tags'] for tag in tags)]
    
    if validated_due_before:
        filtered_tasks = [task for task in filtered_tasks 
                         if task['due'] and task['due'] <= validated_due_before]
    
    # Sort tasks
    if sort_by == "due":
        filtered_tasks.sort(key=lambda x: (
            x['due'] is None,  # Tasks without due date come last
            x['due'] or '',    # Then sort by due date
            x['id']            # Finally by ID for stability
        ))
    elif sort_by == "created":
        filtered_tasks.sort(key=lambda x: (x['created_at'], x['id']))
    elif sort_by == "title":
        filtered_tasks.sort(key=lambda x: (x['title'].lower(), x['id']))
    
    return filtered_tasks

def complete_task(path: str, task_id: int) -> bool:
    """
    Mark a task as completed.
    
    Args:
        path: Path to the JSON file
        task_id: ID of the task to complete
        
    Returns:
        True if task was found and updated, False otherwise
    """
    tasks = _read_tasks(path)
    
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = True
            _write_tasks(path, tasks)
            return True
    
    return False

def update_task(path: str, task_id: int, **fields: Any) -> bool:
    """
    Update task fields.
    
    Args:
        path: Path to the JSON file
        task_id: ID of the task to update
        **fields: Fields to update (title, tags, due)
        
    Returns:
        True if task was found and updated, False otherwise
        
    Raises:
        ValueError: If any field validation fails
    """
    tasks = _read_tasks(path)
    
    for task in tasks:
        if task['id'] == task_id:
            # Update fields if provided
            if 'title' in fields:
                if not fields['title'] or not fields['title'].strip():
                    raise ValueError("Title cannot be empty")
                task['title'] = fields['title'].strip()
            
            if 'tags' in fields:
                task['tags'] = _validate_tags(fields['tags'])
            
            if 'due' in fields:
                task['due'] = _validate_date(fields['due'])
            
            _write_tasks(path, tasks)
            return True
    
    return False

def delete_task(path: str, task_id: int) -> bool:
    """
    Delete a task.
    
    Args:
        path: Path to the JSON file
        task_id: ID of the task to delete
        
    Returns:
        True if task was found and deleted, False otherwise
    """
    tasks = _read_tasks(path)
    
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            del tasks[i]
            _write_tasks(path, tasks)
            return True
    
    return False