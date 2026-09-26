# TICKET-004: Completion rate

## Summary

Add `TaskService.completion_rate() -> float`.

## Acceptance criteria

- Percentage (0-100) of tasks that are done, rounded to 1 decimal place.
- An empty board returns `0.0` (SPEC §3).
- Tests included, including the empty board.
