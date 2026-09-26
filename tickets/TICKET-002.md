# TICKET-002: Overdue and due-soon tasks

## Summary

Surface tasks that are late or coming up.

## Acceptance criteria

- `TaskService.list_overdue(today: date) -> list[Task]`: **not done** and `due_date` **strictly before** `today` (SPEC §3). A task due today is not overdue.
- `TaskService.list_due_soon(today: date, days: int = 3) -> list[Task]`: not done and `today <= due_date <= today + days`. `days < 0` raises `ValueError`.
- Tasks with no due date are never overdue or due soon.
- `TaskService.overdue_report(today: date) -> str`: returns `No overdue tasks.` when empty; otherwise a header `N overdue task(s):` followed by one line per task `- #<id> <title> (due YYYY-MM-DD, N day(s) late)`, sorted by due date ascending.
- Tests included.
