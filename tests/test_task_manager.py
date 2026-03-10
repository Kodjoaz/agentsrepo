"""Unit and integration tests for the Task Manager.

Phase 4 — Testing
Agent: QA / Test Agent
Input: design.md, src/task_manager.py, src/storage.py, src/cli.py
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.storage import Storage
from src.task_manager import Task, TaskManager
from src.cli import build_parser, run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class InMemoryStorage:
    """Stub storage that keeps data in a Python list — no file system required."""

    def __init__(self, initial: list[dict] | None = None):
        self._data: list[dict] = initial or []

    def load(self) -> list[dict]:
        return list(self._data)

    def save(self, tasks: list[dict]) -> None:
        self._data = list(tasks)


# ===========================================================================
# Task dataclass tests
# ===========================================================================


class TestTaskDataclass(unittest.TestCase):
    """FR-02, FR-03: Task id and timestamps are set on creation."""

    def test_to_dict_roundtrip(self):
        task = Task(id=1, title="Write tests", description="Important!", due_date="2026-12-31")
        restored = Task.from_dict(task.to_dict())
        self.assertEqual(restored.id, task.id)
        self.assertEqual(restored.title, task.title)
        self.assertEqual(restored.description, task.description)
        self.assertEqual(restored.due_date, task.due_date)
        self.assertEqual(restored.status, task.status)
        self.assertEqual(restored.created_at, task.created_at)

    def test_default_status_is_pending(self):
        task = Task(id=1, title="Test")
        self.assertEqual(task.status, "pending")

    def test_from_dict_missing_optional_fields(self):
        minimal = {"id": 5, "title": "Minimal", "created_at": "2026-01-01T00:00:00+00:00"}
        task = Task.from_dict(minimal)
        self.assertEqual(task.description, "")
        self.assertIsNone(task.due_date)
        self.assertEqual(task.status, "pending")


# ===========================================================================
# TaskManager — business logic tests
# ===========================================================================


class TestTaskManagerAdd(unittest.TestCase):
    """FR-01, FR-02: Adding tasks."""

    def setUp(self):
        self.manager = TaskManager(InMemoryStorage())

    def test_add_returns_task(self):
        task = self.manager.add_task("Buy milk")
        self.assertIsInstance(task, Task)
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.id, 1)

    def test_add_increments_id(self):
        t1 = self.manager.add_task("First")
        t2 = self.manager.add_task("Second")
        self.assertEqual(t2.id, t1.id + 1)

    def test_add_strips_whitespace_from_title(self):
        task = self.manager.add_task("  padded title  ")
        self.assertEqual(task.title, "padded title")

    def test_add_empty_title_raises(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("")

    def test_add_whitespace_only_title_raises(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_add_with_description_and_due_date(self):
        task = self.manager.add_task("Design DB", description="ERD first", due_date="2026-06-01")
        self.assertEqual(task.description, "ERD first")
        self.assertEqual(task.due_date, "2026-06-01")


class TestTaskManagerList(unittest.TestCase):
    """FR-05, FR-06: Listing and filtering tasks."""

    def setUp(self):
        self.manager = TaskManager(InMemoryStorage())
        self.manager.add_task("Task A")
        self.manager.add_task("Task B")
        self.manager.add_task("Task C")
        self.manager.complete_task(2)

    def test_list_all(self):
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 3)

    def test_list_sorted_by_id(self):
        ids = [t.id for t in self.manager.list_tasks()]
        self.assertEqual(ids, sorted(ids))

    def test_filter_pending(self):
        tasks = self.manager.list_tasks(status_filter="pending")
        self.assertTrue(all(t.status == "pending" for t in tasks))
        self.assertEqual(len(tasks), 2)

    def test_filter_done(self):
        tasks = self.manager.list_tasks(status_filter="done")
        self.assertTrue(all(t.status == "done" for t in tasks))
        self.assertEqual(len(tasks), 1)

    def test_list_empty_manager(self):
        empty = TaskManager(InMemoryStorage())
        self.assertEqual(empty.list_tasks(), [])


class TestTaskManagerComplete(unittest.TestCase):
    """FR-07, FR-08: Completing tasks."""

    def setUp(self):
        self.manager = TaskManager(InMemoryStorage())
        self.task = self.manager.add_task("Write code")

    def test_complete_sets_status_done(self):
        updated = self.manager.complete_task(self.task.id)
        self.assertEqual(updated.status, "done")

    def test_complete_is_idempotent(self):
        self.manager.complete_task(self.task.id)
        updated = self.manager.complete_task(self.task.id)
        self.assertEqual(updated.status, "done")

    def test_complete_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.manager.complete_task(999)


class TestTaskManagerRemove(unittest.TestCase):
    """FR-09, FR-10: Removing tasks."""

    def setUp(self):
        self.manager = TaskManager(InMemoryStorage())
        self.task = self.manager.add_task("Delete me")

    def test_remove_decreases_count(self):
        self.manager.remove_task(self.task.id)
        self.assertEqual(len(self.manager.list_tasks()), 0)

    def test_remove_returns_task(self):
        removed = self.manager.remove_task(self.task.id)
        self.assertEqual(removed.id, self.task.id)

    def test_remove_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.manager.remove_task(999)

    def test_next_id_after_removal(self):
        """IDs keep incrementing even after a gap is created by removal."""
        self.manager.remove_task(self.task.id)
        new_task = self.manager.add_task("After gap")
        self.assertGreater(new_task.id, self.task.id)


# ===========================================================================
# Storage layer — integration tests
# ===========================================================================


class TestStorage(unittest.TestCase):
    """FR-11, FR-12: JSON file persistence."""

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._store_path = os.path.join(self._tmp_dir, "tasks.json")

    def _make_storage(self) -> Storage:
        return Storage(self._store_path)

    def test_load_missing_file_returns_empty(self):
        storage = self._make_storage()
        self.assertEqual(storage.load(), [])

    def test_save_and_load_roundtrip(self):
        tasks = [{"id": 1, "title": "Persisted task", "status": "pending"}]
        storage = self._make_storage()
        storage.save(tasks)
        loaded = storage.load()
        self.assertEqual(loaded, tasks)

    def test_save_overwrites_previous(self):
        storage = self._make_storage()
        storage.save([{"id": 1, "title": "Old"}])
        storage.save([{"id": 1, "title": "New"}])
        self.assertEqual(storage.load()[0]["title"], "New")

    def test_load_corrupt_file_raises_runtime_error(self):
        with open(self._store_path, "w") as fh:
            fh.write("NOT JSON!!!")
        storage = self._make_storage()
        with self.assertRaises(RuntimeError):
            storage.load()

    def test_tasks_persist_across_manager_instances(self):
        """FR-11: data survives process restarts (simulated by re-instantiation)."""
        storage1 = self._make_storage()
        mgr1 = TaskManager(storage1)
        mgr1.add_task("Persistent task")

        storage2 = self._make_storage()
        mgr2 = TaskManager(storage2)
        tasks = mgr2.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Persistent task")


# ===========================================================================
# CLI layer tests
# ===========================================================================


class TestCLI(unittest.TestCase):
    """FR-13: CLI commands."""

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._store_path = os.path.join(self._tmp_dir, "test_tasks.json")

    def _run(self, *args):
        return run(list(args), store_path=self._store_path)

    def test_add_command_exits_zero(self):
        rc = self._run("add", "CLI task")
        self.assertEqual(rc, 0)

    def test_list_command_exits_zero(self):
        rc = self._run("list")
        self.assertEqual(rc, 0)

    def test_list_with_status_filter(self):
        self._run("add", "Task 1")
        rc = self._run("list", "--status", "pending")
        self.assertEqual(rc, 0)

    def test_complete_command_exits_zero(self):
        self._run("add", "Finish me")
        rc = self._run("complete", "1")
        self.assertEqual(rc, 0)

    def test_remove_command_exits_zero(self):
        self._run("add", "Remove me")
        rc = self._run("remove", "1")
        self.assertEqual(rc, 0)

    def test_add_empty_title_exits_nonzero(self):
        rc = self._run("add", "")
        self.assertEqual(rc, 1)

    def test_complete_missing_id_exits_nonzero(self):
        rc = self._run("complete", "99")
        self.assertEqual(rc, 1)

    def test_remove_missing_id_exits_nonzero(self):
        rc = self._run("remove", "99")
        self.assertEqual(rc, 1)

    def test_add_with_description_and_due(self):
        rc = self._run("add", "Task with extras", "--description", "Desc", "--due", "2026-12-31")
        self.assertEqual(rc, 0)

    def test_end_to_end_workflow(self):
        """AC-01: add → list → complete → remove."""
        self._run("add", "End-to-end task")
        self._run("complete", "1")
        tasks_done = TaskManager(Storage(self._store_path)).list_tasks(status_filter="done")
        self.assertEqual(len(tasks_done), 1)
        self._run("remove", "1")
        tasks_all = TaskManager(Storage(self._store_path)).list_tasks()
        self.assertEqual(len(tasks_all), 0)


# ===========================================================================
# Parser tests
# ===========================================================================


class TestCLIParser(unittest.TestCase):
    """Verify that argparse is configured correctly."""

    def setUp(self):
        self.parser = build_parser()

    def test_add_parses_title(self):
        ns = self.parser.parse_args(["add", "My task"])
        self.assertEqual(ns.title, "My task")

    def test_add_parses_description(self):
        ns = self.parser.parse_args(["add", "T", "--description", "Desc"])
        self.assertEqual(ns.description, "Desc")

    def test_add_parses_due_date(self):
        ns = self.parser.parse_args(["add", "T", "--due", "2026-06-01"])
        self.assertEqual(ns.due_date, "2026-06-01")

    def test_list_default_status_is_none(self):
        ns = self.parser.parse_args(["list"])
        self.assertIsNone(ns.status)

    def test_list_status_pending(self):
        ns = self.parser.parse_args(["list", "--status", "pending"])
        self.assertEqual(ns.status, "pending")

    def test_complete_parses_id(self):
        ns = self.parser.parse_args(["complete", "42"])
        self.assertEqual(ns.id, 42)

    def test_remove_parses_id(self):
        ns = self.parser.parse_args(["remove", "7"])
        self.assertEqual(ns.id, 7)


if __name__ == "__main__":
    unittest.main()
