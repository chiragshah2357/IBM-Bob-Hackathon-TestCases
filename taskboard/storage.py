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
        self._conn.create_function("casefold", 1, _casefold, deterministic=True)
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

    def search(
        self,
        query: str,
        *,
        tag: str | None = None,
        include_done: bool = True,
    ) -> list[Task]:
        """Return tasks whose title contains ``query``, ignoring case.

        Args:
            query: Text to look for anywhere in the title. ``%`` and ``_``
                are matched literally, not as wildcards.
            tag: If given, only tasks carrying this tag are returned. Tags
                are compared case-insensitively and must match exactly.
            include_done: If False, completed tasks are left out.

        Returns:
            The matching tasks.
        """
        logger.debug(
            "searching tasks: query=%r tag=%r include_done=%s", query, tag, include_done
        )
        pattern = _escape_like(query.casefold())
        sql = f"""
            SELECT * FROM tasks
            WHERE casefold(title) LIKE '%{pattern}%' ESCAPE '\\'
              AND (:include_done OR done = 0)
              AND (:tag IS NULL OR EXISTS (
                  SELECT 1 FROM json_each(tasks.tags)
                  WHERE casefold(json_each.value) = :tag
              ))
            ORDER BY title
        """
        params = {
            "include_done": int(include_done),
            "tag": tag.casefold() if tag is not None else None,
        }
        rows = self._conn.execute(sql, params).fetchall()
        logger.debug("search for %r matched %d task(s)", query, len(rows))
        return [_row_to_task(r) for r in rows]


def _casefold(value: object) -> object:
    """Unicode-aware lower-casing, registered as the SQL function ``casefold``.

    SQLite's own ``lower()`` and ``LIKE`` only fold ASCII letters, so a title
    such as ``"ÄRGER"`` would not match ``"ärger"`` without this. Values that
    are not text (for example ``NULL``) are returned unchanged.
    """
    if isinstance(value, str):
        return value.casefold()
    return value


def _escape_like(value: str) -> str:
    """Escape ``value`` so a LIKE pattern matches it literally.

    Backslashes are doubled first, then the ``%`` and ``_`` wildcards are
    prefixed with a backslash. The query must declare backslash as its
    ``ESCAPE`` character.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        priority=row["priority"],
        due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
        done=bool(row["done"]),
        tags=json.loads(row["tags"]),
    )
