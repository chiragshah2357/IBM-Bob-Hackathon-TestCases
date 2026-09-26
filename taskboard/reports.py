"""Plain-text reports built from tasks."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from taskboard.models import Task

EMPTY_OVERDUE_REPORT = "No overdue tasks."


@dataclass(frozen=True)
class OverdueEntry:
    """A single task as it appears in the overdue report."""

    task_id: int
    title: str
    due_date: date
    days_late: int

    @classmethod
    def from_task(cls, task: Task, today: date) -> OverdueEntry:
        """Build a report entry for ``task`` relative to ``today``.

        Raises ValueError if the task has not been stored yet or has no due date.
        """
        if task.id is None:
            raise ValueError("task must be stored before it can be reported")
        if task.due_date is None:
            raise ValueError(f"task #{task.id} has no due date")
        return cls(
            task_id=task.id,
            title=task.title,
            due_date=task.due_date,
            days_late=(today - task.due_date).days,
        )

    def render(self) -> str:
        """Return the entry formatted as one report line."""
        return (
            f"- #{self.task_id} {self.title} "
            f"(due {self.due_date.isoformat()}, {self.days_late} day(s) late)"
        )


def format_overdue_report(entries: Iterable[OverdueEntry]) -> str:
    """Render overdue entries as a report sorted by due date ascending.

    Entries sharing a due date are ordered by task id so the output is stable.
    Returns ``EMPTY_OVERDUE_REPORT`` when there are no entries.
    """
    ordered = sorted(entries, key=lambda entry: (entry.due_date, entry.task_id))
    if not ordered:
        return EMPTY_OVERDUE_REPORT
    lines = [f"{len(ordered)} overdue task(s):"]
    lines.extend(entry.render() for entry in ordered)
    return "\n".join(lines)
