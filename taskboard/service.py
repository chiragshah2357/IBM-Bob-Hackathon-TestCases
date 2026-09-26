"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

from taskboard.formatting import format_task_detail
from taskboard.models import Task
from taskboard.storage import TaskNotFoundError, TaskRepository

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

    def describe(self, task_id: int) -> str:
        """Return a multi-line, human-readable description of one task.

        Raises TaskNotFoundError if no task has ``task_id``.
        """
        try:
            task = self._repo.get(task_id)
        except TaskNotFoundError:
            logger.warning("cannot describe task %s: not found", task_id)
            raise
        logger.debug("describing task %s", task_id)
        return format_task_detail(task)
