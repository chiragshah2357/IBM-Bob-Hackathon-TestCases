# TICKET-010: Paginate task list

## Summary

Large boards need paging.

## Acceptance criteria

- `TaskRepository.count() -> int`.
- `Page` dataclass: `items`, `page`, `page_size`, `total`, with properties `total_pages` and `has_next`.
- `TaskRepository.list_page(page: int, page_size: int) -> Page`. Pages are **1-indexed**: page 1 returns the first `page_size` tasks by id (SPEC §3).
- `page < 1`, `page_size < 1` or `page_size > 100` raise `ValueError`. A page past the end returns an empty `items` list.
- `TaskService.list_tasks_page(page: int = 1, page_size: int = 20) -> Page`.
- Tests included.
