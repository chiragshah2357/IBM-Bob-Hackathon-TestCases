"""Small helpers shared across Taskboard."""

from __future__ import annotations

import re
from datetime import date, timedelta

MAX_RELATIVE_DAYS = 365

# Named shortcuts accepted by parse_date, mapped to their offset from today.
_KEYWORD_OFFSETS: dict[str, int] = {
    "today": 0,
    "tomorrow": 1,
}

# Shape check only: date.fromisoformat does the calendar validation, but on
# Python 3.11+ it also accepts forms such as "20261001" that SPEC §6 does not.
_ISO_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_RELATIVE_RE = re.compile(r"\+([0-9]+)d")


def parse_date(value: str, today: date | None = None) -> date:
    """Parse a user-supplied due date.

    Accepted forms (case-insensitive, surrounding whitespace ignored):

    - ISO ``YYYY-MM-DD``, e.g. ``2026-10-01``
    - ``today`` and ``tomorrow``
    - ``+Nd``: N days from today, where 0 <= N <= ``MAX_RELATIVE_DAYS``

    ``today`` defaults to ``date.today()`` and is only used by the relative
    forms. Raises ValueError for anything else.
    """
    text = value.strip().lower()
    if today is None:
        today = date.today()

    if text in _KEYWORD_OFFSETS:
        return _shift(today, _KEYWORD_OFFSETS[text])

    offset_match = _RELATIVE_RE.fullmatch(text)
    if offset_match is not None:
        return _shift(today, _parse_offset(offset_match.group(1), value))

    if _ISO_DATE_RE.fullmatch(text) is not None:
        return _parse_iso(text)

    raise ValueError(
        f"unrecognised date {value!r}: expected YYYY-MM-DD, 'today', 'tomorrow' or '+Nd'"
    )


def format_relative(due: date, today: date) -> str:
    """Describe ``due`` relative to ``today`` in plain words.

    Returns ``today``, ``tomorrow`` or ``yesterday`` for adjacent days,
    ``in N days`` for later dates and ``N days ago`` for earlier ones.
    """
    delta = (due - today).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "tomorrow"
    if delta == -1:
        return "yesterday"
    if delta > 0:
        return f"in {delta} days"
    return f"{-delta} days ago"


def _parse_offset(digits: str, original: str) -> int:
    """Convert the N of ``+Nd`` to an int, enforcing the allowed range."""
    days = int(digits)
    if not 0 <= days <= MAX_RELATIVE_DAYS:
        raise ValueError(
            f"relative date {original!r} must be between +0d and +{MAX_RELATIVE_DAYS}d"
        )
    return days


def _parse_iso(text: str) -> date:
    """Parse a ``YYYY-MM-DD`` string, rejecting impossible calendar dates."""
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid calendar date {text!r}") from exc


def _shift(start: date, days: int) -> date:
    """Return ``start`` moved forward by ``days``.

    Raises ValueError when the result falls past ``date.max``.
    """
    try:
        return start + timedelta(days=days)
    except OverflowError as exc:
        raise ValueError(
            f"{start.isoformat()} + {days} days is past the last supported date"
        ) from exc
