"""Domain model for Taskboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

MIN_PRIORITY = 1
MAX_PRIORITY = 5


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
