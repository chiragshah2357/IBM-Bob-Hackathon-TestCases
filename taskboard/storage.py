"""SQLite persistence for tasks."""

from __future__ import annotations

import json
import sqlite3
from datetime import date

from taskboard.models import Task


class TaskNotFoundError(LookupError):
    """Raised when a task id does not exist."""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL,
    priority  INTEGER NOT NULL,
    due_date  TEXT,
    done      INTEGER NOT NULL DEFAULT 0,
    tags      TEXT    NOT NULL DEFAULT '[]'
)
"""


class TaskRepository:
    """Stores tasks in a SQLite database."""

    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_SCHEMA)

    def add(self, task: Task) -> Task:
        """Insert a new task and return it with its id set."""
        cur = self._conn.execute(
            "INSERT INTO tasks (title, priority, due_date, done, tags) VALUES (?, ?, ?, ?, ?)",
            (
                task.title,
                task.priority,
                task.due_date.isoformat() if task.due_date else None,
                int(task.done),
                json.dumps(task.tags),
            ),
        )
        self._conn.commit()
        task.id = cur.lastrowid
        return task

    def get(self, task_id: int) -> Task:
        """Return the task with ``task_id`` or raise TaskNotFoundError."""
        row = self._conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return _row_to_task(row)

    def list_all(self) -> list[Task]:
        """Return every task ordered by id."""
        rows = self._conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [_row_to_task(r) for r in rows]

    def update(self, task: Task) -> None:
        """Persist changes to an existing task."""
        cur = self._conn.execute(
            "UPDATE tasks SET title = ?, priority = ?, due_date = ?, done = ?, tags = ? WHERE id = ?",
            (
                task.title,
                task.priority,
                task.due_date.isoformat() if task.due_date else None,
                int(task.done),
                json.dumps(task.tags),
                task.id,
            ),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise TaskNotFoundError(task.id)


    def list_page(self, page: int, page_size: int) -> list[Task]:
        """Return one page of tasks ordered by id. Pages are 1-indexed."""
        if page < 1 or page_size < 1:
            raise ValueError("page and page_size must be >= 1")
        offset = page * page_size
        rows = self._conn.execute(
            "SELECT * FROM tasks ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        ).fetchall()
        return [_row_to_task(r) for r in rows]


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        priority=row["priority"],
        due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
        done=bool(row["done"]),
        tags=json.loads(row["tags"]),
    )
