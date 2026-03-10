# Design: Task Manager Application

> **Phase**: Design  
> **Agent**: Software Architect Agent  
> **Input**: `requirements.md`  
> **Generated**: Multi-Agent Software Development Sample

---

## 1. Architecture Overview

The application follows a **layered architecture** with three layers:

```
┌─────────────────────────────────────┐
│          CLI Layer (cli.py)          │  ← Parses arguments, calls service layer
├─────────────────────────────────────┤
│       Service Layer (task_manager.py)│  ← Business logic, validation
├─────────────────────────────────────┤
│      Storage Layer (storage.py)      │  ← JSON file persistence
└─────────────────────────────────────┘
```

---

## 2. Module Breakdown

| Module | Responsibility |
|--------|----------------|
| `src/task_manager.py` | Core domain model (`Task`) and service class (`TaskManager`). Contains all business rules. |
| `src/storage.py` | Thin adapter that reads/writes a JSON file. Isolated so it can be swapped (e.g., SQLite). |
| `src/cli.py` | `argparse`-based entry point. Delegates all logic to `TaskManager`. |

---

## 3. Class Design

### 3.1 `Task` (dataclass)

```python
@dataclass
class Task:
    id: int
    title: str
    description: str
    due_date: str | None       # ISO 8601 string or None
    status: str                # "pending" | "done"
    created_at: str            # ISO 8601 datetime string
```

**Serialisation contract**: A `Task` can be converted to/from a plain `dict` for JSON storage via `to_dict()` / `Task.from_dict()` class methods.

### 3.2 `TaskManager`

```python
class TaskManager:
    def __init__(self, storage: Storage) -> None: ...
    def add_task(self, title, description="", due_date=None) -> Task: ...
    def list_tasks(self, status_filter=None) -> list[Task]: ...
    def complete_task(self, task_id: int) -> Task: ...
    def remove_task(self, task_id: int) -> Task: ...
```

**Invariants**:
- `add_task` raises `ValueError` for an empty title.
- `complete_task` and `remove_task` raise `KeyError` when the ID is not found.
- IDs are monotonically increasing integers starting at `1`; gaps may appear after removal.

### 3.3 `Storage`

```python
class Storage:
    def __init__(self, filepath: str) -> None: ...
    def load(self) -> list[dict]: ...
    def save(self, tasks: list[dict]) -> None: ...
```

The `Storage` class reads and writes JSON atomically using a write-then-rename pattern (write to a `.tmp` file, then `os.replace`).

---

## 4. Data Flow

### Add Task

```
CLI → TaskManager.add_task(title)
        → validates title
        → creates Task(id=next_id, ...)
        → storage.save(all_tasks_as_dicts)
        → returns Task
```

### Complete Task

```
CLI → TaskManager.complete_task(id)
        → looks up task by id
        → sets task.status = "done"
        → storage.save(...)
        → returns updated Task
```

---

## 5. Error Handling Strategy

| Scenario | Exception | Caught by |
|----------|-----------|-----------|
| Empty task title | `ValueError` | CLI layer — prints user-friendly message |
| Unknown task ID | `KeyError` | CLI layer — prints user-friendly message |
| Corrupt JSON file | `json.JSONDecodeError` | Storage layer — re-raises as `RuntimeError` |

---

## 6. File Layout

```
agentsrepo/
├── requirements.md        # Phase 1 — Requirements
├── design.md              # Phase 2 — Design (this file)
├── src/
│   ├── __init__.py
│   ├── task_manager.py    # Phase 3 — Core implementation
│   ├── storage.py         # Phase 3 — Persistence
│   └── cli.py             # Phase 3 — CLI entry point
├── tests/
│   ├── __init__.py
│   └── test_task_manager.py  # Phase 4 — Unit tests
└── README.md
```

---

## 7. Testing Strategy

| Level | Scope | Tool |
|-------|-------|------|
| Unit | `Task`, `TaskManager` (in-memory) | `unittest` / `pytest` |
| Integration | `Storage` round-trip | `pytest` + `tmp_path` fixture |
| CLI smoke test | End-to-end argument parsing | `subprocess` / `pytest` |

All tests run with `pytest tests/`.
