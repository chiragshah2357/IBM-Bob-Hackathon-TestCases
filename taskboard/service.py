"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import date

from taskboard.models import DEFAULT_PRIORITY, MAX_PRIORITY, MIN_PRIORITY, Task
from taskboard.storage import TaskNotFoundError, TaskRepository

logger = logging.getLogger(__name__)


def _validate_priority(priority: int) -> int:
    """Return ``priority`` if it is a valid priority level.

    Levels run from ``MIN_PRIORITY`` (most urgent) to ``MAX_PRIORITY``
    (least urgent), see SPEC §1. ``bool`` is rejected even though it is a
    subclass of ``int``, so ``True`` cannot slip through as priority 1.

    Raises ValueError for non-integers and out-of-range values (SPEC §2).
    """
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValueError(f"priority must be an int, not {type(priority).__name__}")
    if not MIN_PRIORITY <= priority < MAX_PRIORITY:
        raise ValueError(
            f"priority must be between {MIN_PRIORITY} and {MAX_PRIORITY}, got {priority}"
        )
    return priority


class TaskService:
    """Application-level operations on tasks."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def create_task(
        self,
        title: str,
        priority: int = DEFAULT_PRIORITY,
        due_date: date | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Create and store a new task.

        Raises ValueError if the title is blank or the priority is not a
        valid level (SPEC §1).
        """
        title = title.strip()
        if not title:
            raise ValueError("title must not be blank")
        priority = _validate_priority(priority)
        task = Task(title=title, priority=priority, due_date=due_date, tags=list(tags or []))
        logger.info("creating task %r with priority %d", title, priority)
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

    def set_priority(self, task_id: int, priority: int) -> Task:
        """Change the priority of an existing task.

        Args:
            task_id: Id of the task to update.
            priority: New priority, from 1 (highest) to 5 (lowest).

        Returns:
            The task with its new priority.

        Raises:
            ValueError: If ``priority`` is not a valid level.
            TaskNotFoundError: If ``task_id`` does not exist.
        """
        priority = _validate_priority(priority)
        task = self._get_task(task_id)
        return self._save_priority(task, priority)

    def bump_priority(self, task_id: int) -> Task:
        """Make a task one level more urgent.

        A task already at the highest priority (1) is returned unchanged.

        Args:
            task_id: Id of the task to bump.

        Returns:
            The task with its new priority.

        Raises:
            TaskNotFoundError: If ``task_id`` does not exist.
        """
        task = self._get_task(task_id)
        return self._save_priority(task, max(MIN_PRIORITY, task.priority - 1))

    def list_by_priority(self) -> list[Task]:
        """Return open (not done) tasks, most urgent first.

        Tasks with the same priority are ordered by id.
        """
        return self._repo.list_open_by_priority()

    def _get_task(self, task_id: int) -> Task:
        """Return the stored task, logging a warning if it does not exist."""
        try:
            return self._repo.get(task_id)
        except TaskNotFoundError:
            logger.warning("task %s not found", task_id)
            raise

    def _save_priority(self, task: Task, priority: int) -> Task:
        """Persist ``priority`` for ``task`` and return the updated copy.

        Nothing is written when the priority is unchanged.
        """
        if task.priority == priority:
            logger.debug("task %s already has priority %d", task.id, priority)
            return task
        self._repo.update_priority(task.id, priority)
        logger.info("task %s priority changed from %d to %d", task.id, task.priority, priority)
        return replace(task, priority=priority)
