# TICKET-011: Bulk status changes

## Summary

Change the status of many tasks at once.

## Acceptance criteria

- `TaskService.complete_all_with_tag(tag: str) -> int`: completes open tasks with the tag (case-insensitive) and returns how many changed. Tasks already done are not counted.
- `TaskService.complete_many(task_ids: list[int]) -> int`: if any id is missing raise `TaskNotFoundError` and change nothing (SPEC §3).
- `TaskService.reopen_task(task_id: int) -> Task`.
- Follow STYLE_GUIDE: snake_case, type hints, docstrings, no bare except.
- Tests included.
