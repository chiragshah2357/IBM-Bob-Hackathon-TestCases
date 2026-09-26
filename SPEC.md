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
| `tags`     | list[str]       | Always lowercase, trimmed, no duplicates. |

## 2. Errors

- Invalid input (blank title, out-of-range priority, bad date, bad page number) → `ValueError`.
- An operation on a task id that does not exist → `TaskNotFoundError` (from `taskboard.storage`).
  Operations must **never** fail silently on a missing id.

## 3. Behaviour rules

- **Overdue**: a task is overdue when it is **not done** and its `due_date` is **strictly before** today.
  A task due today is not overdue.
- **Completion rate**: percentage (0–100) of tasks that are done, rounded to one decimal place.
  An empty board has a completion rate of `0.0`.
- **Pagination**: pages are **1-indexed**. Page 1 returns the first `page_size` tasks ordered by id.
- **Search**: case-insensitive substring match on title.

## 4. Security

- All SQL must use parameterized queries. Never build SQL with string formatting.
- Secrets (tokens, keys) are read from environment variables only. No secrets in source code,
  and no hard-coded fallback values.

## 5. Exports

- CSV exports must be valid RFC 4180 CSV (use Python's `csv` module) so titles containing commas
  or quotes round-trip correctly.
