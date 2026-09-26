from datetime import date, timedelta

import pytest

from taskboard.utils import MAX_RELATIVE_DAYS, format_relative, parse_date

TODAY = date(2026, 9, 26)


def test_parse_date_iso_ignores_today():
    assert parse_date("2026-10-01", today=TODAY) == date(2026, 10, 1)


def test_parse_date_iso_strips_whitespace():
    assert parse_date("  2026-10-01\n", today=TODAY) == date(2026, 10, 1)


def test_parse_date_iso_leap_day():
    assert parse_date("2028-02-29", today=TODAY) == date(2028, 2, 29)


@pytest.mark.parametrize("value", ["today", "TODAY", "  Today  "])
def test_parse_date_today(value):
    assert parse_date(value, today=TODAY) == TODAY


@pytest.mark.parametrize("value", ["tomorrow", "Tomorrow", "\ttomorrow "])
def test_parse_date_tomorrow(value):
    assert parse_date(value, today=TODAY) == date(2026, 9, 27)


def test_parse_date_tomorrow_crosses_year_end():
    assert parse_date("tomorrow", today=date(2026, 12, 31)) == date(2027, 1, 1)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("+0d", TODAY),
        ("+1d", date(2026, 9, 27)),
        ("+5d", date(2026, 10, 1)),
        ("+7D", date(2026, 10, 3)),
        ("  +10d  ", date(2026, 10, 6)),
    ],
)
def test_parse_date_relative_days(value, expected):
    assert parse_date(value, today=TODAY) == expected


def test_parse_date_relative_upper_bound_is_inclusive():
    assert parse_date(f"+{MAX_RELATIVE_DAYS}d", today=TODAY) == TODAY + timedelta(days=365)


def test_parse_date_relative_past_upper_bound_rejected():
    with pytest.raises(ValueError):
        parse_date(f"+{MAX_RELATIVE_DAYS + 1}d", today=TODAY)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "yesterday",
        "next week",
        "-1d",
        "+d",
        "+1",
        "1d",
        "+1w",
        "+ 1d",
        "++1d",
        "today!",
        "2026/10/01",
        "20261001",
        "2026-W40-4",
        "26-10-01",
        "2026-10-01T00:00",
    ],
)
def test_parse_date_rejects_unsupported_forms(value):
    with pytest.raises(ValueError):
        parse_date(value, today=TODAY)


@pytest.mark.parametrize("value", ["2026-13-01", "2026-02-30", "2027-02-29", "0000-01-01"])
def test_parse_date_rejects_impossible_calendar_dates(value):
    with pytest.raises(ValueError):
        parse_date(value, today=TODAY)


@pytest.mark.parametrize("value", ["tomorrow", "+1d"])
def test_parse_date_past_last_supported_date_raises_value_error(value):
    with pytest.raises(ValueError):
        parse_date(value, today=date.max)


def test_parse_date_zero_offset_on_last_supported_date():
    assert parse_date("+0d", today=date.max) == date.max


def test_parse_date_defaults_today_to_current_date():
    before = date.today()
    result = parse_date("today")
    after = date.today()
    assert result in (before, after)


@pytest.mark.parametrize(
    ("due", "expected"),
    [
        (TODAY, "today"),
        (date(2026, 9, 27), "tomorrow"),
        (date(2026, 9, 25), "yesterday"),
        (date(2026, 9, 28), "in 2 days"),
        (date(2026, 9, 24), "2 days ago"),
        (date(2026, 10, 26), "in 30 days"),
        (date(2025, 8, 22), "400 days ago"),
    ],
)
def test_format_relative(due, expected):
    assert format_relative(due, TODAY) == expected


def test_format_relative_across_year_boundary():
    assert format_relative(date(2027, 1, 1), date(2026, 12, 31)) == "tomorrow"
    assert format_relative(date(2026, 12, 30), date(2027, 1, 1)) == "2 days ago"


def test_format_relative_round_trips_parse_date():
    due = parse_date("+14d", today=TODAY)
    assert format_relative(due, TODAY) == "in 14 days"
