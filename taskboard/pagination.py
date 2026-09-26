"""Pagination primitives shared by the storage and service layers."""

from __future__ import annotations

from dataclasses import dataclass

from taskboard.models import Task

FIRST_PAGE = 1
DEFAULT_PAGE_SIZE = 20


def validate_page_args(page: int, page_size: int) -> None:
    """Check that ``page`` and ``page_size`` describe a valid page request.

    Pages are 1-indexed. Raises ValueError if either value is not a positive
    integer.
    """
    _require_int("page", page)
    _require_int("page_size", page_size)
    if page < FIRST_PAGE:
        raise ValueError(f"page must be >= {FIRST_PAGE}, got {page}")
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")


def _require_int(name: str, value: object) -> None:
    """Raise ValueError unless ``value`` is a real ``int``.

    ``bool`` is rejected explicitly: it subclasses ``int``, but a call such as
    ``list_page(True, 10)`` is always a caller mistake.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {value!r}")


@dataclass
class Page:
    """One page of tasks from a listing ordered by id.

    ``page`` is 1-indexed and ``total`` counts every task in the listing, not
    just the ones in ``items``.
    """

    items: list[Task]
    page: int
    page_size: int
    total: int

    def __post_init__(self) -> None:
        """Reject page metadata that could not describe a real listing."""
        validate_page_args(self.page, self.page_size)
        if self.total < 0:
            raise ValueError(f"total must be >= 0, got {self.total}")

    @property
    def total_pages(self) -> int:
        """Number of pages needed to hold ``total`` tasks; 0 for an empty listing."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """True when at least one more page follows this one."""
        return self.page < self.total_pages
