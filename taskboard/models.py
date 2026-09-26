"""Domain model for Taskboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

MIN_PRIORITY = 1
MAX_PRIORITY = 5

UNSAVED_ID_LABEL = "?"


@dataclass
class Task:
    """A single to-do item.

    Priority runs from 1 (highest) to 5 (lowest).
    """

    title: str
    priority: int = 3
    due_date: date | None = None
    done: bool = False
    tags: list[str] = field(default_factory=list)
    id: int | None = None

    @property
    def id_label(self) -> str:
        """Return the id as display text, or ``"?"`` for a task that is not stored yet."""
        return UNSAVED_ID_LABEL if self.id is None else str(self.id)

    def summary(self) -> str:
        """Return a one-line, human-readable summary of the task.

        The format is ``[x] #<id> <title> (P<priority>)`` for a done task and
        ``[ ] #<id> <title> (P<priority>)`` for an open one. When the task has a due
        date it is added inside the parentheses, e.g. ``(P2, due 2026-10-01)``.
        """
        checkbox = "[x]" if self.done else "[ ]"
        details = f"P{self.priority}"
        if self.due_date is not None:
            details += f", due {self.due_date.isoformat()}"
        return f"{checkbox} #{self.id_label} {self.title} ({details})"
