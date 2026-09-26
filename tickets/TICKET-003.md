# TICKET-003: Validate task priority

## Summary

`TaskService.create_task` must validate `priority`.

## Acceptance criteria

- Accept 1 to 5 **inclusive** (SPEC §1).
- Raise `ValueError` for anything outside that range.
- Tests for both boundaries (1 and 5) and for invalid values.
