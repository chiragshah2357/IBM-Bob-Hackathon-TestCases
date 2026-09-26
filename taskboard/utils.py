"""Small helpers shared across Taskboard."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date


def parse_date(value: str) -> date:
    """Parse an ISO ``YYYY-MM-DD`` string into a date.

    Raises ValueError for anything else.
    """
    return date.fromisoformat(value.strip())


def normalize_tag(tag: str) -> str:
    """Return ``tag`` in the canonical form it is stored in.

    Tag comparisons are case-insensitive (SPEC §1), so the canonical form is
    the tag with surrounding whitespace removed and every letter lowercased:
    ``"  Work "`` becomes ``"work"``.

    Args:
        tag: The tag as supplied by the caller.

    Returns:
        The trimmed, lowercased tag.

    Raises:
        ValueError: If the tag is empty or contains only whitespace.
    """
    cleaned = tag.strip()
    if not cleaned:
        raise ValueError("tag must not be blank")
    return cleaned.lower()


def normalize_tags(tags: Iterable[str]) -> list[str]:
    """Normalize a collection of tags and drop duplicates.

    Every tag goes through :func:`normalize_tag`. When several inputs
    normalize to the same value only the first one is kept, so
    ``["Home", "work", "HOME"]`` becomes ``["home", "work"]``.

    Args:
        tags: The tags as supplied by the caller, in any letter case.

    Returns:
        The normalized tags in first-seen order, without duplicates.

    Raises:
        ValueError: If any tag is blank. The message names its position.
    """
    normalized: list[str] = []
    for position, raw in enumerate(tags):
        try:
            normalized.append(normalize_tag(raw))
        except ValueError as exc:
            raise ValueError(f"tag at position {position} is invalid: {raw!r}") from exc
    return list(dict.fromkeys(normalized))
