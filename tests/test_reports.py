from datetime import date

import pytest

from taskboard.models import Task
from taskboard.reports import EMPTY_OVERDUE_REPORT, OverdueEntry, format_overdue_report

TODAY = date(2026, 9, 26)


def test_from_task_computes_days_late():
    task = Task(title="Pay rent", due_date=date(2026, 9, 16), id=4)
    entry = OverdueEntry.from_task(task, TODAY)
    assert entry == OverdueEntry(task_id=4, title="Pay rent", due_date=date(2026, 9, 16), days_late=10)


def test_from_task_counts_days_across_month_boundary():
    task = Task(title="Renew visa", due_date=date(2026, 8, 30), id=1)
    assert OverdueEntry.from_task(task, TODAY).days_late == 27


def test_from_task_rejects_unsaved_task():
    with pytest.raises(ValueError):
        OverdueEntry.from_task(Task(title="Draft", due_date=date(2026, 9, 1)), TODAY)


def test_from_task_rejects_task_without_due_date():
    with pytest.raises(ValueError):
        OverdueEntry.from_task(Task(title="Someday", id=2), TODAY)


def test_render_formats_line():
    entry = OverdueEntry(task_id=7, title="Fix leak, kitchen", due_date=date(2026, 9, 1), days_late=25)
    assert entry.render() == "- #7 Fix leak, kitchen (due 2026-09-01, 25 day(s) late)"


def test_format_overdue_report_empty():
    assert format_overdue_report([]) == EMPTY_OVERDUE_REPORT == "No overdue tasks."


def test_format_overdue_report_breaks_due_date_ties_by_id():
    entries = [
        OverdueEntry(task_id=5, title="b", due_date=date(2026, 9, 20), days_late=6),
        OverdueEntry(task_id=3, title="a", due_date=date(2026, 9, 20), days_late=6),
        OverdueEntry(task_id=9, title="c", due_date=date(2026, 9, 10), days_late=16),
    ]
    assert format_overdue_report(entries).splitlines() == [
        "3 overdue task(s):",
        "- #9 c (due 2026-09-10, 16 day(s) late)",
        "- #3 a (due 2026-09-20, 6 day(s) late)",
        "- #5 b (due 2026-09-20, 6 day(s) late)",
    ]


def test_format_overdue_report_accepts_generator():
    due_dates = [date(2026, 9, 12), date(2026, 9, 5)]
    entries = (
        OverdueEntry(task_id=i, title=f"task {i}", due_date=due, days_late=(TODAY - due).days)
        for i, due in enumerate(due_dates, start=1)
    )
    assert format_overdue_report(entries).splitlines() == [
        "2 overdue task(s):",
        "- #2 task 2 (due 2026-09-05, 21 day(s) late)",
        "- #1 task 1 (due 2026-09-12, 14 day(s) late)",
    ]
