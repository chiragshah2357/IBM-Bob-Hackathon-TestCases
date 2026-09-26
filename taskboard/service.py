"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from taskboard.models import Task
from taskboard.reports import OverdueEntry, format_overdue_report
from taskboard.storage import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """Application-level operations on tasks."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def create_task(
        self,
        title: str,
        priority: int = 3,
        due_date: date | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Create and store a new task.

        Raises ValueError if the title is blank.
        """
        title = title.strip()
        if not title:
            raise ValueError("title must not be blank")
        task = Task(title=title, priority=priority, due_date=due_date, tags=list(tags or []))
        logger.info("creating task %r", title)
        return self._repo.add(task)

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as done and return it."""
        task = self._repo.get(task_id)
        task.done = True
        self._repo.update(task)
        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks ordered by id."""
        return self._repo.list_all()

    def list_overdue(self, today: date) -> list[Task]:
        """Return tasks that are past their due date as of ``today``, ordered by id.

        Tasks without a due date are never overdue.
        Raises ValueError if ``today`` is not a ``datetime.date``.
        """
        today = _require_date(today, "today")
        overdue = [
            task
            for task in self._repo.list_all()
            if task.due_date is not None and task.due_date <= today
        ]
        logger.info("found %d overdue task(s) as of %s", len(overdue), today)
        return overdue

    def list_due_soon(self, today: date, days: int = 3) -> list[Task]:
        """Return open tasks due between ``today`` and ``today + days`` inclusive.

        Results are ordered by id. Tasks without a due date are never due soon.
        Raises ValueError if ``today`` is not a ``datetime.date``, if ``days`` is
        negative, or if the window would run past the last representable date.
        """
        today = _require_date(today, "today")
        if days < 0:
            raise ValueError(f"days must be >= 0, got {days}")
        try:
            horizon = today + timedelta(days=days)
        except OverflowError as exc:
            raise ValueError(f"days={days} extends the window past {date.max}") from exc
        due_soon = [
            task
            for task in self._repo.list_all()
            if not task.done and task.due_date is not None and today <= task.due_date <= horizon
        ]
        logger.info("found %d task(s) due between %s and %s", len(due_soon), today, horizon)
        return due_soon

    def overdue_report(self, today: date) -> str:
        """Return a plain-text summary of overdue tasks, earliest due date first.

        Returns ``No overdue tasks.`` when nothing is overdue; otherwise a
        ``N overdue task(s):`` header followed by one line per task.
        """
        entries = [OverdueEntry.from_task(task, today) for task in self.list_overdue(today)]
        logger.info("building overdue report for %d task(s)", len(entries))
        return format_overdue_report(entries)


def _require_date(value: object, name: str) -> date:
    """Return ``value`` unchanged if it is a calendar date, else raise ValueError.

    ``datetime`` is rejected explicitly: it subclasses ``date`` but cannot be
    compared with the plain ``date`` values stored on tasks.
    """
    if isinstance(value, datetime) or not isinstance(value, date):
        raise ValueError(f"{name} must be a datetime.date, got {type(value).__name__}")
    return value
