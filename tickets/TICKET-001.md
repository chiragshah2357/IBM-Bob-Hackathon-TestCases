# TICKET-001: Search tasks

## Summary

Users need to find tasks by title, optionally narrowed by tag and status.

## Acceptance criteria

- `TaskRepository.search(query: str, *, tag: str | None = None, include_done: bool = True) -> list[Task]`.
- Case-insensitive substring match on title.
- Optional `tag` filter: case-insensitive exact tag match.
- `include_done=False` excludes completed tasks.
- Results ordered by id (SPEC §3).
- Parameterized SQL only (SPEC §4).
- `TaskService.search_tasks(query, tag=None, include_done=True)` strips the query; a blank query raises `ValueError`.
- Tests included.
