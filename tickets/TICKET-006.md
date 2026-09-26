# TICKET-006: Delete a task

## Summary

Add `TaskRepository.delete(task_id: int) -> None` and `TaskService.delete_task(task_id: int) -> None`.

## Acceptance criteria

- Deletes the task.
- Deleting a missing id raises `TaskNotFoundError` (SPEC §2: never fail silently).
- Tests for both the success case and the missing-id case.
