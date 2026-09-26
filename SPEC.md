# Taskboard — Product Specification

Taskboard is a small Python library for tracking to-do items. It is used by
internal tools, so correctness and predictable errors matter more than features.

## 1. Task model

| Field      | Type            | Rules |
|------------|-----------------|-------|
| `id`       | int             | Assigned by storage on insert. |
| `title`    | str             | Required. Leading/trailing whitespace is stripped. Blank titles are rejected. |
| `priority` | int             | **1 (highest) to 5 (lowest), inclusive.** Default 3. |
| `due_date` | date or None    | Optional. ISO `YYYY-MM-DD` when serialized. |
| `done`     | bool            | Default False. |
| `tags`     | list[str]       | Always lowercase, trimmed, no duplicates. **Tag comparisons are case-insensitive.** |

## 2. Errors

- Invalid input (blank title, out-of-range priority, bad date, bad page number) → `ValueError`.
- An operation on a task id that does not exist → `TaskNotFoundError` (from `taskboard.storage`).
  Operations must **never** fail silently on a missing id.
- Missing required configuration → `RuntimeError`.

## 3. Behaviour rules

- **Overdue**: a task is overdue when it is **not done** and its `due_date` is **strictly before** today.
  A task due today is not overdue.
- **Due soon**: a task is due soon when it is **not done** and `today <= due_date <= today + days`.
- **Completion rate**: percentage (0–100) of tasks that are done, rounded to one decimal place.
  An empty board has a completion rate of `0.0`.
- **Pagination**: pages are **1-indexed**. Page 1 returns the first `page_size` tasks ordered by id.
  `page_size` must be between 1 and 100 inclusive. A page past the end returns no items.
- **Search**: case-insensitive substring match on title. Results are **ordered by id**.
- **Bulk operations** validate every id before changing anything: if any id is missing, nothing is changed.

## 4. Security & configuration

- All SQL must use parameterized queries. Never build SQL with string formatting.
- Secrets (tokens, keys) are read from environment variables only. No secrets in source code,
  and no hard-coded fallback values.
- Environment variables:

| Variable | Default | Rules |
|----------|---------|-------|
| `TASKBOARD_DB_PATH` | `taskboard.db` | |
| `TASKBOARD_LOG_LEVEL` | `INFO` | One of DEBUG, INFO, WARNING, ERROR (case-insensitive). Anything else → `ValueError`. |
| `TASKBOARD_EXPORT_URL` | `https://hooks.example.com/taskboard` | |
| `TASKBOARD_EXPORT_TOKEN` | *(none — required)* | Missing or empty → `RuntimeError`. |

## 5. Exports

- CSV exports must be valid RFC 4180 CSV (use Python's `csv` module) so titles containing commas
  or quotes round-trip correctly. Tags are joined with `;`.
- JSON exports are a list of objects with ISO dates, UTF-8, indented by 2 spaces.

## 6. Dates

- `parse_date` accepts ISO `YYYY-MM-DD`, `today`, `tomorrow`, and `+Nd` (N days from today, 0 ≤ N ≤ 365),
  case-insensitive with surrounding whitespace ignored. Anything else → `ValueError`.
