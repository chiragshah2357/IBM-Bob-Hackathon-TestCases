# TICKET-009: Task summaries and table view

## Summary

Human-readable output for CLIs and logs.

## Acceptance criteria

- `Task.summary() -> str`: `[x] #<id> <title> (P<priority>)` when done, `[ ]` when not done; with a due date: `(P2, due 2026-10-01)`.
- `format_task_table(tasks: list[Task]) -> str` in `taskboard/formatting.py`: columns `ID`, `Done`, `Pri`, `Due`, `Title`; header row, a separator row of dashes, one row per task; column widths fit the content. An empty list returns `(no tasks)`.
- `TaskService.describe(task_id: int) -> str`: multi-line detail of one task; missing id raises `TaskNotFoundError`.
- Tests included.
