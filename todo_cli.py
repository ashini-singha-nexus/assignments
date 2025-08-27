"""
CLI interface for JSON-backed TODO system with tags and due dates.

This module provides a command-line interface for managing TODO tasks
stored in a JSON file with filtering, sorting, and CRUD operations.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from todo_core import (
    add_task, list_tasks, complete_task, update_task, delete_task,
    _is_past_due, _validate_date, _validate_tags
)

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="JSON-backed TODO system with tags and due dates")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title of the task")
    add_parser.add_argument("--tags", help="Comma-separated list of tags")
    add_parser.add_argument("--due", help="Due date in YYYY-MM-DD format")
    add_parser.add_argument("--allow-past-due", action="store_true", 
                           help="Allow past due dates without warning")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks with optional filtering")
    list_parser.add_argument("--status", choices=["open", "done"], help="Filter by status")
    list_parser.add_argument("--tags", help="Comma-separated list of tags to filter by")
    list_parser.add_argument("--due-before", help="Filter by due date before this date (YYYY-MM-DD)")
    list_parser.add_argument("--sort-by", choices=["due", "created", "title"], 
                            default="due", help="Sort field")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("task_id", type=int, help="ID of the task to update")
    update_parser.add_argument("--title", help="New title for the task")
    update_parser.add_argument("--tags", help="New comma-separated list of tags")
    update_parser.add_argument("--due", help="New due date in YYYY-MM-DD format")
    update_parser.add_argument("--allow-past-due", action="store_true", 
                              help="Allow past due dates without warning")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")
    
    # Common arguments
    for p in [add_parser, list_parser, complete_parser, update_parser, delete_parser]:
        p.add_argument("--file", default="todo.json", help="Path to JSON file (default: todo.json)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Execute the appropriate command
        if args.command == "add":
            handle_add(args)
        elif args.command == "list":
            handle_list(args)
        elif args.command == "complete":
            handle_complete(args)
        elif args.command == "update":
            handle_update(args)
        elif args.command == "delete":
            handle_delete(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_add(args: argparse.Namespace) -> None:
    """Handle the add command."""
    # Check for past due date warning
    if args.due and not args.allow_past_due and _is_past_due(args.due):
        response = input(f"Warning: Due date {args.due} is in the past. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Task creation cancelled.")
            return
    
    task = add_task(args.file, args.title, args.tags, args.due)
    print(f"Added task #{task['id']}: {task['title']}")

def handle_list(args: argparse.Namespace) -> None:
    """Handle the list command."""
    tags = _validate_tags(args.tags) if args.tags else None
    
    tasks = list_tasks(
        args.file, 
        status=args.status, 
        tags=tags, 
        due_before=args.due_before, 
        sort_by=args.sort_by
    )
    
    if not tasks:
        print("No tasks found.")
        return
    
    # Format and display tasks
    for task in tasks:
        status = "✓" if task['done'] else " "
        due_info = f" due:{task['due']}" if task['due'] else ""
        tags_info = f" tags:{','.join(task['tags'])}" if task['tags'] else ""
        print(f"{task['id']:3d} [{status}] {task['title']}{due_info}{tags_info}")

def handle_complete(args: argparse.Namespace) -> None:
    """Handle the complete command."""
    if complete_task(args.file, args.task_id):
        print(f"Completed task #{args.task_id}")
    else:
        print(f"Task #{args.task_id} not found", file=sys.stderr)
        sys.exit(1)

def handle_update(args: argparse.Namespace) -> None:
    """Handle the update command."""
    # Check for past due date warning
    if args.due and not args.allow_past_due and _is_past_due(args.due):
        response = input(f"Warning: Due date {args.due} is in the past. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Task update cancelled.")
            return
    
    # Prepare update fields
    update_fields = {}
    if args.title is not None:
        update_fields['title'] = args.title
    if args.tags is not None:
        update_fields['tags'] = args.tags
    if args.due is not None:
        update_fields['due'] = args.due
    
    if update_task(args.file, args.task_id, **update_fields):
        print(f"Updated task #{args.task_id}")
    else:
        print(f"Task #{args.task_id} not found", file=sys.stderr)
        sys.exit(1)

def handle_delete(args: argparse.Namespace) -> None:
    """Handle the delete command."""
    if delete_task(args.file, args.task_id):
        print(f"Deleted task #{args.task_id}")
    else:
        print(f"Task #{args.task_id} not found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()