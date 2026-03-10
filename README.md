# agentsrepo — Multi-Agent Software Development Sample

A demonstration of **multi-agent software development**: a team of AI agents
collaborates to take a feature from raw requirements all the way through design,
implementation, and automated testing.

---

## Agents & Phases

| Phase | Agent | Artefact |
|-------|-------|----------|
| 1 — Requirements | Requirements Analyst Agent | [`requirements.md`](requirements.md) |
| 2 — Design | Software Architect Agent | [`design.md`](design.md) |
| 3 — Implementation | Implementation Agent | `src/` |
| 4 — Testing | QA / Test Agent | `tests/` |

---

## The Sample Application: Task Manager

A lightweight command-line **Task Manager** built with the Python standard
library only. It supports creating, listing, completing, and removing tasks, with
JSON-file persistence.

### Quick Start

```bash
# Add tasks
python -m src.cli add "Buy groceries" --description "Milk and eggs" --due 2026-03-15
python -m src.cli add "Write report"

# List all tasks
python -m src.cli list

# Filter by status
python -m src.cli list --status pending
python -m src.cli list --status done

# Complete a task
python -m src.cli complete 1

# Remove a task
python -m src.cli remove 2
```

### Running the Tests

```bash
pip install pytest          # one-time setup
pytest tests/ -v
```

Expected output: **43 tests, all passing**.

---

## Project Layout

```
agentsrepo/
├── requirements.md          # Phase 1 — What to build
├── design.md                # Phase 2 — How to build it
├── src/
│   ├── task_manager.py      # Phase 3 — Domain model & business logic
│   ├── storage.py           # Phase 3 — JSON persistence layer
│   └── cli.py               # Phase 3 — argparse CLI entry point
└── tests/
    └── test_task_manager.py # Phase 4 — 43 unit & integration tests
```