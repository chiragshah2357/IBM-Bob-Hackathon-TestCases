# TICKET-005: Tag management

## Summary

Full tag support on tasks.

## Acceptance criteria

- `normalize_tag(tag: str) -> str` in `taskboard/utils.py`: strip + lowercase; blank raises `ValueError`.
- `create_task` normalizes tags and drops duplicates, keeping first-seen order.
- `TaskService.add_tag(task_id: int, tag: str) -> Task`: normalized; adding a tag that already exists **in any letter case** is a no-op (SPEC §1).
- `TaskService.remove_tag(task_id: int, tag: str) -> Task`: **case-insensitive**; removing an absent tag is a no-op.
- `TaskService.list_tags() -> list[str]`: all distinct tags across tasks, sorted.
- `TaskService.tasks_with_tag(tag: str) -> list[Task]`: case-insensitive, ordered by id.
- Missing task ids raise `TaskNotFoundError`. Changes are persisted.
- Tests included.
