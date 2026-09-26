# TICKET-008: Export tasks to CSV

## Summary

Add `taskboard/export.py` with `export_csv(tasks: list[Task], path: str) -> int` returning rows written.

## Acceptance criteria

- Header: `id,title,priority,due_date,done,tags`.
- Tags joined with `;`.
- Must produce valid CSV via the `csv` module so titles with commas/quotes round-trip (SPEC §5).
- Follow STYLE_GUIDE (logging, not print).
- Tests included.
