"""Board statistics and their human-readable summary."""

from __future__ import annotations

from dataclasses import dataclass

from taskboard.models import MAX_PRIORITY, MIN_PRIORITY

PRIORITIES: tuple[int, ...] = tuple(range(MIN_PRIORITY, MAX_PRIORITY + 1))

_PRIORITY_NOTES: dict[int, str] = {MIN_PRIORITY: "highest", MAX_PRIORITY: "lowest"}


@dataclass
class BoardStats:
    """A snapshot of board health.

    ``by_priority`` maps every priority from 1 to 5 to the number of **open**
    tasks with that priority; priorities without open tasks map to 0.

    Raises ValueError if the numbers are inconsistent with each other.
    """

    total: int
    done: int
    open: int
    completion_rate: float
    by_priority: dict[int, int]

    def __post_init__(self) -> None:
        """Check that the numbers describe a possible board."""
        if min(self.total, self.done, self.open) < 0:
            raise ValueError("task counts must not be negative")
        if self.done + self.open != self.total:
            raise ValueError(
                f"done ({self.done}) + open ({self.open}) must equal total ({self.total})"
            )
        if not 0.0 <= self.completion_rate <= 100.0:
            raise ValueError(
                f"completion_rate must be between 0 and 100, got {self.completion_rate}"
            )
        if sorted(self.by_priority) != list(PRIORITIES):
            raise ValueError(
                f"by_priority must have exactly one entry per priority "
                f"{MIN_PRIORITY}-{MAX_PRIORITY}, got keys {sorted(self.by_priority)}"
            )
        if any(count < 0 for count in self.by_priority.values()):
            raise ValueError("by_priority counts must not be negative")


def _priority_label(priority: int) -> str:
    """Return a display label such as ``P1 (highest)`` or ``P3``."""
    note = _PRIORITY_NOTES.get(priority)
    return f"P{priority} ({note})" if note else f"P{priority}"


def format_stats(stats: BoardStats) -> str:
    """Render ``stats`` as a multi-line, human-readable summary.

    Example output::

        Tasks: 5 total, 2 done, 3 open
        Completion: 40.0%
        Open tasks by priority:
          P1 (highest): 1
          P2: 0
          P3: 2
          P4: 0
          P5 (lowest): 0
    """
    lines = [
        f"Tasks: {stats.total} total, {stats.done} done, {stats.open} open",
        f"Completion: {stats.completion_rate:.1f}%",
        "Open tasks by priority:",
    ]
    lines.extend(
        f"  {_priority_label(priority)}: {stats.by_priority[priority]}" for priority in PRIORITIES
    )
    return "\n".join(lines)
