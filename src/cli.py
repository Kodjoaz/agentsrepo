"""Command-line interface for the Task Manager.

Usage
-----
    python -m src.cli add "Buy groceries" --description "Milk, eggs" --due 2026-03-15
    python -m src.cli list
    python -m src.cli list --status pending
    python -m src.cli complete 1
    python -m src.cli remove 1
"""

import argparse
import sys

from src.storage import Storage
from src.task_manager import TaskManager

DEFAULT_STORE = "tasks.json"


def build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="A simple command-line task manager.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── add ──────────────────────────────────────────────────────────────
    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("title", help="Title of the task.")
    add_parser.add_argument(
        "--description", default="", help="Optional longer description."
    )
    add_parser.add_argument(
        "--due", dest="due_date", default=None, help="Due date in YYYY-MM-DD format."
    )

    # ── list ─────────────────────────────────────────────────────────────
    list_parser = subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument(
        "--status",
        choices=["pending", "done"],
        default=None,
        help="Filter by status.",
    )

    # ── complete ─────────────────────────────────────────────────────────
    complete_parser = subparsers.add_parser("complete", help="Mark a task as done.")
    complete_parser.add_argument("id", type=int, help="ID of the task to complete.")

    # ── remove ───────────────────────────────────────────────────────────
    remove_parser = subparsers.add_parser("remove", help="Remove a task.")
    remove_parser.add_argument("id", type=int, help="ID of the task to remove.")

    # Suppress linter warnings for unused variables (they document the API).
    _ = add_parser, list_parser, complete_parser, remove_parser

    return parser


def run(args=None, store_path: str = DEFAULT_STORE) -> int:
    """Parse *args* and execute the requested command.

    Returns the process exit code (0 on success, 1 on error).
    """
    parser = build_parser()
    ns = parser.parse_args(args)

    storage = Storage(store_path)
    manager = TaskManager(storage)

    try:
        if ns.command == "add":
            task = manager.add_task(ns.title, ns.description, ns.due_date)
            print(f"Added task #{task.id}: {task.title}")

        elif ns.command == "list":
            tasks = manager.list_tasks(ns.status)
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    due = f"  [due: {task.due_date}]" if task.due_date else ""
                    print(f"[{task.status:7}] #{task.id}: {task.title}{due}")

        elif ns.command == "complete":
            task = manager.complete_task(ns.id)
            print(f"Task #{task.id} marked as done.")

        elif ns.command == "remove":
            task = manager.remove_task(ns.id)
            print(f"Task #{task.id} removed.")

    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())
