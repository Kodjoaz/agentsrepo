"""Core domain model and service class for the Task Manager.

Phase 3 — Implementation
Agent: Implementation Agent
Input: design.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------


@dataclass
class Task:
    """Represents a single task."""

    id: int
    title: str
    description: str = ""
    due_date: Optional[str] = None  # ISO 8601 date string or None
    status: str = "pending"  # "pending" | "done"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstruct a :class:`Task` from a plain dict."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )

    def __repr__(self) -> str:  # pragma: no cover
        due = f", due={self.due_date}" if self.due_date else ""
        return f"Task(id={self.id}, title={self.title!r}, status={self.status}{due})"


# ---------------------------------------------------------------------------
# Service layer
# ---------------------------------------------------------------------------


class TaskManager:
    """Business-logic layer for managing tasks.

    Parameters
    ----------
    storage:
        A storage adapter that implements ``load() -> list[dict]`` and
        ``save(tasks: list[dict]) -> None``.
    """

    def __init__(self, storage) -> None:
        self._storage = storage
        self._tasks: dict[int, Task] = {}
        self._max_id: int = 0
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Populate the in-memory cache from persistent storage."""
        raw = self._storage.load()
        self._tasks = {t["id"]: Task.from_dict(t) for t in raw}
        self._max_id = max(self._tasks.keys(), default=0)

    def _save(self) -> None:
        """Flush the in-memory cache to persistent storage."""
        self._storage.save([t.to_dict() for t in self._tasks.values()])

    def _next_id(self) -> int:
        """Return the next available task ID (always strictly greater than any previously assigned ID)."""
        self._max_id += 1
        return self._max_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
    ) -> Task:
        """Create a new task and persist it.

        Parameters
        ----------
        title:
            A non-empty string describing the task.
        description:
            Optional longer description.
        due_date:
            Optional ISO 8601 date string (e.g. ``"2026-12-31"``).

        Returns
        -------
        Task
            The newly created task.

        Raises
        ------
        ValueError
            If *title* is empty or whitespace-only.
        """
        if not title or not title.strip():
            raise ValueError("Task title must not be empty.")
        task = Task(
            id=self._next_id(),
            title=title.strip(),
            description=description,
            due_date=due_date,
        )
        self._tasks[task.id] = task
        self._save()
        return task

    def list_tasks(self, status_filter: Optional[str] = None) -> list[Task]:
        """Return tasks, optionally filtered by status.

        Parameters
        ----------
        status_filter:
            ``"pending"``, ``"done"``, or ``None`` (returns all tasks).

        Returns
        -------
        list[Task]
            Sorted by task ID (ascending).
        """
        tasks = sorted(self._tasks.values(), key=lambda t: t.id)
        if status_filter is not None:
            tasks = [t for t in tasks if t.status == status_filter]
        return tasks

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as done.

        Parameters
        ----------
        task_id:
            The ID of the task to complete.

        Returns
        -------
        Task
            The updated task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.
        """
        task = self._get_or_raise(task_id)
        task.status = "done"
        self._save()
        return task

    def remove_task(self, task_id: int) -> Task:
        """Delete a task permanently.

        Parameters
        ----------
        task_id:
            The ID of the task to remove.

        Returns
        -------
        Task
            The task that was removed.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.
        """
        task = self._get_or_raise(task_id)
        del self._tasks[task_id]
        self._save()
        return task

    def get_task(self, task_id: int) -> Task:
        """Retrieve a single task by ID.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.
        """
        return self._get_or_raise(task_id)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _get_or_raise(self, task_id: int) -> Task:
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        return self._tasks[task_id]
