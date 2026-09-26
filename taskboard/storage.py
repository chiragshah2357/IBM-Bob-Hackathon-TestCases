"""SQLite persistence for tasks."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import date

from taskboard.models import Task

logger = logging.getLogger(__name__)


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

    def delete(self, task_id: int) -> bool:
        """Delete the task with ``task_id``.

        The deletion is committed immediately. Ids are never handed out again
        because the table uses ``AUTOINCREMENT``.

        Returns:
            True if a task was removed, False if no task had that id.
        """
        cur = self._write("DELETE FROM tasks WHERE id = ?", (task_id,))
        removed = cur.rowcount > 0
        logger.debug("delete task %s: %d row(s) removed", task_id, cur.rowcount)
        return removed

    def delete_completed(self) -> int:
        """Delete every task marked done in a single statement.

        Open tasks are left untouched.

        Returns:
            The number of tasks removed; 0 when nothing has been completed.
        """
        cur = self._write("DELETE FROM tasks WHERE done = ?", (1,))
        logger.debug("removed %d completed task(s)", cur.rowcount)
        return cur.rowcount

    def count(self) -> int:
        """Return the total number of stored tasks.

        Open and completed tasks are both counted.
        """
        row = self._conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        return int(row[0])

    def _write(self, sql: str, params: tuple[object, ...]) -> sqlite3.Cursor:
        """Execute one data-changing statement and commit it.

        If SQLite reports an error the open transaction is rolled back before
        the error is re-raised, so the connection stays usable afterwards.
        The cursor is returned so callers can read ``rowcount``.
        """
        try:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
        except sqlite3.Error:
            self._conn.rollback()
            logger.exception("database write failed; transaction rolled back")
            raise
        return cur


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        priority=row["priority"],
        due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
        done=bool(row["done"]),
        tags=json.loads(row["tags"]),
    )
