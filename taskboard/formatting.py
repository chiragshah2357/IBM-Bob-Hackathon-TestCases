"""Human-readable renderings of tasks for CLIs and logs."""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from taskboard.models import Task

logger = logging.getLogger(__name__)

EMPTY_TABLE_TEXT = "(no tasks)"
COLUMN_GAP = "  "
NO_VALUE = "-"


@dataclass(frozen=True)
class _Column:
    """One column of the task table: its header, cell renderer and alignment."""

    header: str
    render: Callable[[Task], str]
    align_right: bool = False

    def pad(self, text: str, width: int) -> str:
        """Pad ``text`` to ``width`` characters using the column's alignment."""
        return text.rjust(width) if self.align_right else text.ljust(width)


def _format_done(task: Task) -> str:
    """Return ``yes`` for a done task and ``no`` for an open one."""
    return "yes" if task.done else "no"


def _format_priority(task: Task) -> str:
    """Return the priority in the ``P<n>`` form used by :meth:`Task.summary`."""
    return f"P{task.priority}"


def _format_due(task: Task) -> str:
    """Return the ISO due date, or ``-`` when the task has none."""
    return task.due_date.isoformat() if task.due_date is not None else NO_VALUE


_COLUMNS: tuple[_Column, ...] = (
    _Column("ID", lambda task: task.id_label, align_right=True),
    _Column("Done", _format_done),
    _Column("Pri", _format_priority),
    _Column("Due", _format_due),
    _Column("Title", lambda task: task.title),
)


def format_task_table(tasks: list[Task]) -> str:
    """Render tasks as a plain-text table for terminals and logs.

    The table has the columns ``ID``, ``Done``, ``Pri``, ``Due`` and ``Title``: a
    header row, a separator row of dashes, then one row per task in the order given.
    Every column is exactly as wide as its longest cell, header included, and columns
    are separated by two spaces. Trailing whitespace is removed from each line.

    An empty list returns ``"(no tasks)"``.
    """
    if not tasks:
        return EMPTY_TABLE_TEXT
    header = [column.header for column in _COLUMNS]
    body = [[column.render(task) for column in _COLUMNS] for task in tasks]
    widths = _column_widths([header, *body])
    separator = ["-" * width for width in widths]
    lines = [_join_cells(row, widths) for row in (header, separator, *body)]
    logger.debug("formatted a table of %d tasks", len(tasks))
    return "\n".join(lines)


def format_task_detail(task: Task) -> str:
    """Render one task as a multi-line block of labelled fields.

    The first line is ``Task #<id>: <title>``; the following indented lines give the
    status (``done`` or ``open``), priority, due date and tags. A missing due date or
    an empty tag list is shown as ``-``.
    """
    fields = (
        ("Status", "done" if task.done else "open"),
        ("Priority", _format_priority(task)),
        ("Due", _format_due(task)),
        ("Tags", ", ".join(task.tags) if task.tags else NO_VALUE),
    )
    label_width = max(len(label) for label, _ in fields) + 1
    lines = [f"Task #{task.id_label}: {task.title}"]
    lines.extend(f"  {(label + ':').ljust(label_width)} {value}" for label, value in fields)
    return "\n".join(lines)


def _column_widths(rows: Sequence[Sequence[str]]) -> list[int]:
    """Return the width of each column: the length of its longest cell in ``rows``."""
    return [max(len(row[index]) for row in rows) for index in range(len(_COLUMNS))]


def _join_cells(cells: Sequence[str], widths: Sequence[int]) -> str:
    """Pad each cell to its column width and join them into one table line."""
    padded = (column.pad(cell, width) for column, cell, width in zip(_COLUMNS, cells, widths))
    return COLUMN_GAP.join(padded).rstrip()
