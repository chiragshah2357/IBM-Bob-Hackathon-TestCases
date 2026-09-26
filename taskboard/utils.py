"""Small helpers shared across Taskboard."""

from __future__ import annotations

from datetime import date


def parse_date(value: str) -> date:
    """Parse an ISO ``YYYY-MM-DD`` string into a date.

    Raises ValueError for anything else.
    """
    return date.fromisoformat(value.strip())
