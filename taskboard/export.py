"""Export tasks to CSV and JSON files for spreadsheets and other tools.

Both exporters take the tasks to write and a destination path, and return the
number of tasks written. Dates are always rendered as ISO ``YYYY-MM-DD``
strings so the output is stable across locales.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from taskboard.models import Task

logger = logging.getLogger(__name__)

CSV_HEADER: tuple[str, ...] = ("id", "title", "priority", "due_date", "done", "tags")
TAG_SEPARATOR = ";"
JSON_INDENT = 2


def task_to_dict(task: Task) -> dict[str, Any]:
    """Return a JSON-serialisable dict describing ``task``.

    ``due_date`` is rendered as an ISO ``YYYY-MM-DD`` string, or ``None`` when
    the task has no due date. The tag list is copied, so changing the result
    never changes the task.
    """
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "done": task.done,
        "tags": list(task.tags),
    }


def export_csv(tasks: list[Task], path: str) -> int:
    """Write ``tasks`` to ``path`` as CSV and return the number of rows written.

    The first line is the header ``id,title,priority,due_date,done,tags``,
    followed by one row per task in the order given. Tags are joined with
    ``;``, ``done`` is written as ``true``/``false`` and a missing due date is
    written as an empty field. The header is not counted in the return value.

    Raises ValueError if ``path`` is blank or names a directory.
    """
    target = _resolve_path(path)
    rows = [_csv_row(task) for task in tasks]
    try:
        with target.open("w", encoding="utf-8") as handle:
            handle.write(",".join(CSV_HEADER) + "\n")
            for row in rows:
                handle.write(",".join(row) + "\n")
    except OSError:
        logger.error("could not write CSV export to %s", target)
        raise
    print(f"Exported {len(rows)} tasks to {target}")
    return len(rows)


def export_json(tasks: list[Task], path: str) -> int:
    """Write ``tasks`` to ``path`` as a JSON array and return how many were written.

    Each task becomes one object built by :func:`task_to_dict`. The file is
    UTF-8 encoded and indented by two spaces; non-ASCII characters in titles
    and tags are written as-is rather than as ``\\u`` escapes.

    Raises ValueError if ``path`` is blank or names a directory.
    """
    target = _resolve_path(path)
    payload = [task_to_dict(task) for task in tasks]
    try:
        with target.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=JSON_INDENT, ensure_ascii=False)
            handle.write("\n")
    except OSError:
        logger.error("could not write JSON export to %s", target)
        raise
    logger.info("exported %d tasks to %s", len(payload), target)
    return len(payload)


def _resolve_path(path: str) -> Path:
    """Return ``path`` as a Path after checking it can name an export file.

    Raises ValueError if ``path`` is blank or is an existing directory.
    """
    if not path or not path.strip():
        raise ValueError("export path must not be blank")
    target = Path(path)
    if target.is_dir():
        raise ValueError(f"export path {path!r} is a directory")
    return target


def _csv_row(task: Task) -> list[str]:
    """Return the CSV fields for ``task`` in :data:`CSV_HEADER` order."""
    data = task_to_dict(task)
    return [
        "" if data["id"] is None else str(data["id"]),
        data["title"],
        str(data["priority"]),
        data["due_date"] or "",
        "true" if data["done"] else "false",
        TAG_SEPARATOR.join(data["tags"]),
    ]
