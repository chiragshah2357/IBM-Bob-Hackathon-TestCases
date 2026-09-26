# TICKET-003: Priority management

## Summary

Validate and manage task priority.

## Acceptance criteria

- `create_task` validates priority: 1 to 5 **inclusive** (SPEC §1); anything else raises `ValueError`.
- `TaskService.set_priority(task_id: int, priority: int) -> Task` with the same validation; missing id raises `TaskNotFoundError`.
- `TaskService.bump_priority(task_id: int) -> Task` makes a task one level more urgent (priority - 1), never going below 1.
- `TaskService.list_by_priority() -> list[Task]`: open (not done) tasks sorted by priority ascending, then id.
- Tests for **both** boundaries (1 and 5), invalid values, and each new method.
