# TICKET-006: Delete tasks

## Summary

Allow removing tasks individually and in bulk.

## Acceptance criteria

- `TaskRepository.delete(task_id: int) -> None`: deleting a missing id raises `TaskNotFoundError` (SPEC §2: never fail silently).
- `TaskRepository.count() -> int`.
- `TaskService.delete_task(task_id: int) -> None`.
- `TaskService.delete_completed() -> int`: deletes every done task and returns how many were removed.
- Tests for the success case, **the missing-id case**, and `delete_completed`.
