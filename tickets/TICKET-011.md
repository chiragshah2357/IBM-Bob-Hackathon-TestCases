# TICKET-011: Bulk-complete tasks by tag

## Summary

Add `TaskService.complete_all_with_tag(tag: str) -> int` returning how many tasks were completed.

## Acceptance criteria

- Tag match is case-insensitive.
- Tasks already done are not counted.
- Follow STYLE_GUIDE: snake_case, type hints, docstring, no bare except.
- Tests included.
