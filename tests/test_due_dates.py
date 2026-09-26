from datetime import date, datetime, timedelta

import pytest

TODAY = date(2026, 9, 26)


def _ids(tasks):
    return [task.id for task in tasks]


def test_list_overdue_returns_past_due_tasks_in_id_order(service):
    recent = service.create_task("File taxes", due_date=date(2026, 9, 20))
    older = service.create_task("Renew passport", due_date=date(2026, 8, 1))
    service.create_task("Plan trip", due_date=date(2026, 10, 15))
    assert _ids(service.list_overdue(TODAY)) == [recent.id, older.id]


def test_list_overdue_includes_task_due_yesterday(service):
    task = service.create_task("Call bank", due_date=TODAY - timedelta(days=1))
    assert _ids(service.list_overdue(TODAY)) == [task.id]


def test_list_overdue_excludes_task_due_tomorrow(service):
    service.create_task("Dentist", due_date=TODAY + timedelta(days=1))
    assert service.list_overdue(TODAY) == []


def test_list_overdue_ignores_tasks_without_due_date(service):
    service.create_task("Someday")
    assert service.list_overdue(TODAY) == []


def test_list_overdue_empty_board(service):
    assert service.list_overdue(TODAY) == []


@pytest.mark.parametrize("bad_today", [datetime(2026, 9, 26, 9, 0), "2026-09-26", None])
def test_list_overdue_rejects_non_date_today(service, bad_today):
    with pytest.raises(ValueError):
        service.list_overdue(bad_today)


def test_list_due_soon_window_is_inclusive(service):
    due_today = service.create_task("Stand-up notes", due_date=TODAY)
    due_last_day = service.create_task("Send invoice", due_date=TODAY + timedelta(days=3))
    service.create_task("Too far out", due_date=TODAY + timedelta(days=4))
    service.create_task("Already late", due_date=TODAY - timedelta(days=1))
    assert _ids(service.list_due_soon(TODAY)) == [due_today.id, due_last_day.id]


def test_list_due_soon_excludes_done_tasks(service):
    booked = service.create_task("Book flights", due_date=TODAY + timedelta(days=1))
    service.complete_task(booked.id)
    pending = service.create_task("Pack bags", due_date=TODAY + timedelta(days=2))
    assert _ids(service.list_due_soon(TODAY)) == [pending.id]


def test_list_due_soon_ignores_tasks_without_due_date(service):
    service.create_task("Someday")
    assert service.list_due_soon(TODAY) == []


def test_list_due_soon_empty_board(service):
    assert service.list_due_soon(TODAY) == []


def test_list_due_soon_custom_days(service):
    near = service.create_task("Review PR", due_date=TODAY + timedelta(days=7))
    service.create_task("Quarterly plan", due_date=TODAY + timedelta(days=8))
    assert _ids(service.list_due_soon(TODAY, days=7)) == [near.id]


def test_list_due_soon_zero_days_means_today_only(service):
    due_today = service.create_task("Water plants", due_date=TODAY)
    service.create_task("Laundry", due_date=TODAY + timedelta(days=1))
    assert _ids(service.list_due_soon(TODAY, days=0)) == [due_today.id]


def test_list_due_soon_rejects_negative_days(service):
    with pytest.raises(ValueError):
        service.list_due_soon(TODAY, days=-1)


def test_list_due_soon_rejects_window_past_max_date(service):
    with pytest.raises(ValueError):
        service.list_due_soon(date.max, days=1)


def test_list_due_soon_rejects_datetime_today(service):
    with pytest.raises(ValueError):
        service.list_due_soon(datetime(2026, 9, 26, 9, 0))


def test_overdue_report_empty_board(service):
    assert service.overdue_report(TODAY) == "No overdue tasks."


def test_overdue_report_when_nothing_is_overdue(service):
    service.create_task("Someday")
    service.create_task("Next week", due_date=TODAY + timedelta(days=7))
    assert service.overdue_report(TODAY) == "No overdue tasks."


def test_overdue_report_sorted_by_due_date(service):
    service.create_task("Submit expenses", due_date=date(2026, 9, 24))
    service.create_task("Renew passport", due_date=date(2026, 9, 1))
    service.create_task("Plan trip", due_date=date(2026, 10, 15))
    assert service.overdue_report(TODAY) == (
        "2 overdue task(s):\n"
        "- #2 Renew passport (due 2026-09-01, 25 day(s) late)\n"
        "- #1 Submit expenses (due 2026-09-24, 2 day(s) late)"
    )


def test_overdue_report_single_task_one_day_late(service):
    service.create_task("Call bank", due_date=TODAY - timedelta(days=1))
    assert service.overdue_report(TODAY) == (
        "1 overdue task(s):\n"
        "- #1 Call bank (due 2026-09-25, 1 day(s) late)"
    )
