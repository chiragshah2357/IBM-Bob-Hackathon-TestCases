# TICKET-001: Search tasks by title

## Summary

Add `TaskRepository.search(query: str) -> list[Task]`.

## Acceptance criteria

- Case-insensitive substring match on title.
- Results ordered by id.
- Must follow SPEC §4: parameterized SQL only.
- Tests included.
