# TICKET-002: List overdue tasks

## Summary

Add `TaskService.list_overdue(today: date) -> list[Task]`.

## Acceptance criteria

- Returns tasks that are **not done** and whose `due_date` is **strictly before** `today` (SPEC §3).
- Tasks with no due date are never overdue.
- A task due today is not overdue.
- Tests included.
