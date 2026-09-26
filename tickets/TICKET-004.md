# TICKET-004: Board statistics

## Summary

A quick health summary of the board.

## Acceptance criteria

- `TaskService.completion_rate() -> float`: percentage (0-100) of done tasks, rounded to 1 decimal place. An empty board returns `0.0` (SPEC §3).
- `BoardStats` dataclass: `total`, `done`, `open`, `completion_rate`, `by_priority: dict[int, int]` (count of **open** tasks for every priority 1-5, including zeros).
- `TaskService.stats() -> BoardStats`.
- `format_stats(stats: BoardStats) -> str`: multi-line human-readable summary.
- Tests included, **including the empty board**.
