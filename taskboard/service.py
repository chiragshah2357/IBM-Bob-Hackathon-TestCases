"""Business logic for Taskboard."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import date

from taskboard.models import MAX_PRIORITY, MIN_PRIORITY, Task
from taskboard.stats import PRIORITIES, BoardStats
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

    def completion_rate(self) -> float:
        """Return the percentage (0-100) of tasks that are done, rounded to one decimal place."""
        tasks = self._repo.list_all()
        return _completion_rate(_count_done(tasks), len(tasks))

    def stats(self) -> BoardStats:
        """Return task counts, the completion rate and open tasks per priority."""
        tasks = self._repo.list_all()
        done = _count_done(tasks)
        board_stats = BoardStats(
            total=len(tasks),
            done=done,
            open=len(tasks) - done,
            completion_rate=_completion_rate(done, len(tasks)),
            by_priority=_count_open_by_priority(tasks),
        )
        logger.debug("board stats: %s", board_stats)
        return board_stats


def _count_done(tasks: Iterable[Task]) -> int:
    """Return how many of ``tasks`` are done."""
    return sum(1 for task in tasks if task.done)


def _completion_rate(done: int, total: int) -> float:
    """Return ``done`` as a percentage of ``total``, rounded to one decimal place."""
    return round(done / total * 100, 1)


def _count_open_by_priority(tasks: Iterable[Task]) -> dict[int, int]:
    """Count open (not done) tasks for every priority from 1 to 5, including zeros.

    Tasks whose priority falls outside 1-5 are logged and left out of the counts.
    """
    counts = {priority: 0 for priority in PRIORITIES}
    for task in tasks:
        if task.done:
            continue
        if task.priority not in counts:
            logger.warning(
                "task #%s has priority %s outside %d-%d; not counted by priority",
                task.id,
                task.priority,
                MIN_PRIORITY,
                MAX_PRIORITY,
            )
            continue
        counts[task.priority] += 1
    return counts
