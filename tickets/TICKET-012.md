# TICKET-012: Relative due dates

## Summary

Let users type due dates naturally.

## Acceptance criteria

- `parse_date(value: str, today: date | None = None) -> date` per SPEC §6 (`today` defaults to `date.today()`).
- `format_relative(due: date, today: date) -> str`: `today`, `tomorrow`, `yesterday`, `in N days`, `N days ago`.
- `TaskService.set_due_date(task_id: int, value: str, today: date | None = None) -> Task` using `parse_date`; missing id raises `TaskNotFoundError`.
- Tests included.
