# TICKET-005: Add a tag to a task

## Summary

Add `TaskService.add_tag(task_id: int, tag: str) -> Task`.

## Acceptance criteria

- Tag is trimmed and lowercased before storing.
- Adding a tag that already exists (in any letter case) is a no-op: no duplicates (SPEC §1).
- Missing task id raises `TaskNotFoundError`.
- Change is persisted.
