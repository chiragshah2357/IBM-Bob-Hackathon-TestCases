"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

from taskboard.models import Task
from taskboard.storage import TaskRepository
from taskboard.utils import parse_date

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

    def set_due_date(self, task_id: int, value: str, today: date | None = None) -> Task:
        """Set a task's due date from user input and return the updated task.

        ``value`` accepts any form understood by ``parse_date``: an ISO
        ``YYYY-MM-DD`` date, ``today``, ``tomorrow`` or ``+Nd``. Relative forms
        are resolved against ``today``, which defaults to the current date.

        Raises ValueError if ``value`` cannot be parsed and TaskNotFoundError
        if ``task_id`` does not exist. The stored task is unchanged on error.
        """
        due = parse_date(value, today)
        task = self._repo.get(task_id)
        task.due_date = due
        self._repo.update(task)
        logger.info("set due date of task %s to %s", task_id, due.isoformat())
        return task
