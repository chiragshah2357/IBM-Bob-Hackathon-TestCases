# Taskboard (IBM Bob Hackathon test cases)

A deliberately small Python task tracker used as a **test bed for automated code review**.

- `SPEC.md` — product specification (the source of truth for behaviour)
- `STYLE_GUIDE.md` — team conventions
- `tickets/` — one ticket per feature; each open pull request implements one ticket
- `taskboard/` — library code
- `tests/` — pytest suite

## Run the tests

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt   # Windows
.venv/Scripts/python -m pytest -q
```

The open pull requests are review targets. Each one implements a ticket from `tickets/`;
some contain problems a reviewer should catch and some are clean.
