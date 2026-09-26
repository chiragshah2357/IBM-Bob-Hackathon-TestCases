# TICKET-007: Export webhook token config

## Summary

Add `taskboard/config.py` with `get_export_token() -> str`.

## Acceptance criteria

- Reads the token from the `TASKBOARD_EXPORT_TOKEN` environment variable.
- If the variable is missing or empty, raise `RuntimeError` with a helpful message.
- No token values in source code (SPEC §4).
- Tests included.
