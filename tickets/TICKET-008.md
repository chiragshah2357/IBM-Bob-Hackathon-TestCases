# TICKET-008: Export tasks

## Summary

Export tasks for spreadsheets and other tools, in `taskboard/export.py`.

## Acceptance criteria

- `task_to_dict(task: Task) -> dict` with ISO date strings.
- `export_csv(tasks: list[Task], path: str) -> int` returns rows written. Header `id,title,priority,due_date,done,tags`; tags joined with `;`. Must be valid CSV via the `csv` module so titles with commas/quotes round-trip (SPEC §5).
- `export_json(tasks: list[Task], path: str) -> int` per SPEC §5.
- Follow STYLE_GUIDE (logging, not print).
- Tests included.
