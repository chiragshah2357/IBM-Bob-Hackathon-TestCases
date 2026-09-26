"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

from taskboard.models import Task
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

    def delete_task(self, task_id: int) -> None:
        """Permanently delete the task with ``task_id``.

        The task is removed from storage straight away and cannot be
        recovered.

        Raises:
            ValueError: if ``task_id`` is not an integer.
        """
        _require_task_id(task_id)
        self._repo.delete(task_id)
        logger.info("deleted task %d", task_id)

    def delete_completed(self) -> int:
        """Delete every done task and return how many were removed.

        Open tasks are kept. Calling this on a board with no completed tasks
        is harmless and returns 0.
        """
        removed = self._repo.delete_completed()
        if removed:
            logger.info(
                "deleted %d completed task(s); %d task(s) remain",
                removed,
                self._repo.count(),
            )
        else:
            logger.debug("no completed tasks to delete")
        return removed


def _require_task_id(task_id: object) -> None:
    """Raise ValueError unless ``task_id`` is an int.

    ``bool`` is rejected explicitly because it is a subclass of ``int`` and
    ``True`` would otherwise be treated as task id 1.
    """
    if isinstance(task_id, bool) or not isinstance(task_id, int):
        raise ValueError(f"task id must be an int, got {task_id!r}")
