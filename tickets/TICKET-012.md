# TICKET-012: Relative due dates

## Summary

Extend `parse_date(value: str, today: date | None = None) -> date`.

## Acceptance criteria

- Accept `today` and `tomorrow` (case-insensitive) relative to the `today` argument (defaults to `date.today()`).
- ISO `YYYY-MM-DD` still works.
- Anything else raises `ValueError`.
- Tests included.
