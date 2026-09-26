# TICKET-010: Paginate task list

## Summary

Add `TaskRepository.list_page(page: int, page_size: int) -> list[Task]`.

## Acceptance criteria

- Pages are **1-indexed**: page 1 returns the first `page_size` tasks by id (SPEC §3).
- `page < 1` or `page_size < 1` raises `ValueError`.
- Tests included.
