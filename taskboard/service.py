"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from datetime import date

from taskboard.models import Task
from taskboard.pagination import DEFAULT_PAGE_SIZE, FIRST_PAGE, Page
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

    def list_tasks_page(
        self,
        page: int = FIRST_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page:
        """Return one page of tasks ordered by id.

        Pages are 1-indexed and a page past the end has no items.
        Raises ValueError for an invalid ``page`` or ``page_size``.
        """
        result = self._repo.list_page(page, page_size)
        logger.debug(
            "listed page %d of %d (%d task(s) in total)",
            result.page,
            result.total_pages,
            result.total,
        )
        return result
