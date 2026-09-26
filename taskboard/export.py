"""Export tasks to other formats."""

from __future__ import annotations

from taskboard.models import Task

HEADER = ["id", "title", "priority", "due_date", "done", "tags"]


def export_csv(tasks: list[Task], path: str) -> int:
    """Write ``tasks`` to ``path`` as CSV and return the number of rows written."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(HEADER) + "\n")
        for t in tasks:
            row = [
                str(t.id),
                t.title,
                str(t.priority),
                t.due_date.isoformat() if t.due_date else "",
                str(t.done),
                ";".join(t.tags),
            ]
            f.write(",".join(row) + "\n")
    print(f"Exported {len(tasks)} tasks to {path}")
    return len(tasks)
