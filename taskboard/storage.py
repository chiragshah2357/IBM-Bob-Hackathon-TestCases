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

    def update_priority(self, task_id: int, priority: int) -> None:
        """Set the priority of an existing task.

        Only the ``priority`` column is written; every other field is left
        untouched. The value is stored as given, since range checks belong
        to the service layer.

        Args:
            task_id: Id of the task to change.
            priority: New priority level.

        Raises:
            TaskNotFoundError: If ``task_id`` does not exist.
        """
        cur = self._conn.execute(
            "UPDATE tasks SET priority = ? WHERE id = ?",
            (priority, task_id),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise TaskNotFoundError(task_id)

    def list_open_by_priority(self) -> list[Task]:
        """Return tasks that are not done, most urgent first.

        Tasks are ordered by priority ascending (1 = most urgent), with ties
        broken by id so the order is stable.
        """
        rows = self._conn.execute(
            "SELECT * FROM tasks WHERE done = 0 ORDER BY priority, id"
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
