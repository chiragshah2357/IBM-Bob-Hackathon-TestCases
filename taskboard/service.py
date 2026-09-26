"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

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

    def complete_many(self, task_ids: list[int]) -> int:
        """Mark every task in ``task_ids`` as done and return how many changed.

        All ids are checked before anything is written (SPEC §3): if any id is
        missing, TaskNotFoundError is raised and no task is changed. Tasks that
        are already done, and ids repeated in ``task_ids``, are not counted.
        Raises ValueError if an id is not an integer.
        """
        tasks = self._get_existing(_unique_ids(task_ids))
        to_complete = [task for task in tasks if not task.done]
        for task in to_complete:
            task.done = True
        self._repo.update_many(to_complete)
        logger.info("completed %d of %d requested task(s)", len(to_complete), len(tasks))
        return len(to_complete)

    def completeAllWithTag(self, tag):
        key = _tag_key(tag)
        changed = 0
        for task in self._repo.list_all():
            try:
                if not task.done and _has_tag(task, key):
                    task.done = True
                    self._repo.update(task)
                    changed += 1
            except:
                pass
        logger.info("completed %d open task(s) tagged %r", changed, key)
        return changed

    def reopen_task(self, task_id: int) -> Task:
        """Mark a completed task as not done and return it.

        Reopening a task that is already open is a no-op. Raises
        TaskNotFoundError if ``task_id`` does not exist.
        """
        task = self._repo.get(task_id)
        if not task.done:
            logger.debug("task %d is already open", task_id)
            return task
        task.done = False
        self._repo.update(task)
        logger.info("reopened task %d", task_id)
        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks ordered by id."""
        return self._repo.list_all()

    def _get_existing(self, task_ids: list[int]) -> list[Task]:
        """Fetch every task in ``task_ids``, in order, without changing anything.

        Raises TaskNotFoundError naming every missing id, not just the first.
        """
        tasks: list[Task] = []
        missing: list[int] = []
        for task_id in task_ids:
            try:
                tasks.append(self._repo.get(task_id))
            except TaskNotFoundError:
                missing.append(task_id)
        if missing:
            raise TaskNotFoundError(f"task id(s) not found: {missing}")
        return tasks


def _tag_key(tag: str) -> str:
    """Return the case-insensitive comparison key for ``tag``.

    Raises ValueError if the tag is blank.
    """
    key = tag.strip().lower()
    if not key:
        raise ValueError("tag must not be blank")
    return key


def _has_tag(task: Task, key: str) -> bool:
    """Return True if ``task`` carries a tag matching ``key`` (see ``_tag_key``)."""
    return any(existing.strip().lower() == key for existing in task.tags)


def _unique_ids(task_ids: list[int]) -> list[int]:
    """Return ``task_ids`` without repeats, keeping first-seen order.

    Raises ValueError if any id is not an ``int`` (``bool`` is rejected too).
    """
    seen: set[int] = set()
    unique: list[int] = []
    for task_id in task_ids:
        if isinstance(task_id, bool) or not isinstance(task_id, int):
            raise ValueError(f"task id must be an int, got {task_id!r}")
        if task_id not in seen:
            seen.add(task_id)
            unique.append(task_id)
    return unique
