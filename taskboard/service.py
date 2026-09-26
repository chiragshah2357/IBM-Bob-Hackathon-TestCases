"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

from taskboard.models import Task
from taskboard.storage import TaskRepository
from taskboard.utils import normalize_tag, normalize_tags

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

        Tags are normalized (trimmed and lowercased) and duplicates are
        dropped, keeping the first occurrence of each tag.

        Raises ValueError if the title or any tag is blank.
        """
        title = title.strip()
        if not title:
            raise ValueError("title must not be blank")
        clean_tags = normalize_tags(tags or [])
        task = Task(title=title, priority=priority, due_date=due_date, tags=clean_tags)
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

    def add_tag(self, task_id: int, tag: str) -> Task:
        """Attach ``tag`` to a task and return the updated task.

        The tag is normalized with :func:`normalize_tag` before it is stored.
        Adding a tag the task already carries, in any letter case, is a no-op.

        Raises:
            TaskNotFoundError: If no task has ``task_id``.
            ValueError: If the tag is blank.
        """
        task = self._repo.get(task_id)
        tag = tag.strip()
        if tag in task.tags:
            logger.debug("task %d already tagged %r", task_id, tag)
            return task
        task.tags.append(normalize_tag(tag))
        self._repo.update(task)
        logger.info("tagged task %d with %r", task_id, tag)
        return task

    def remove_tag(self, task_id: int, tag: str) -> Task:
        """Detach ``tag`` from a task and return the updated task.

        Matching is case-insensitive. Removing a tag the task does not carry
        is a no-op.

        Raises:
            TaskNotFoundError: If no task has ``task_id``.
        """
        task = self._repo.get(task_id)
        remaining = [existing for existing in task.tags if existing != tag]
        if len(remaining) == len(task.tags):
            logger.debug("task %d has no tag %r; nothing to remove", task_id, tag)
            return task
        task.tags = remaining
        self._repo.update(task)
        logger.info("removed tag %r from task %d", tag, task_id)
        return task

    def list_tags(self) -> list[str]:
        """Return every distinct tag used across all tasks, sorted alphabetically.

        An empty board, or a board whose tasks have no tags, returns ``[]``.
        """
        distinct = {tag for task in self._repo.list_all() for tag in task.tags}
        return sorted(distinct)

    def tasks_with_tag(self, tag: str) -> list[Task]:
        """Return the tasks that carry ``tag``, ordered by id.

        Matching is case-insensitive, so ``"Work"`` finds tasks tagged
        ``"work"``. A tag no task carries returns ``[]``.

        Raises:
            ValueError: If the tag is blank.
        """
        wanted = normalize_tag(tag)
        matches = [task for task in self._repo.list_all() if wanted in task.tags]
        logger.debug("found %d task(s) tagged %r", len(matches), wanted)
        return matches
