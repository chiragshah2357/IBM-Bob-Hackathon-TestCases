from datetime import date

from taskboard.models import Task


def test_summary_not_done_without_due_date():
    assert Task(title="Buy milk", priority=2, id=3).summary() == "[ ] #3 Buy milk (P2)"


def test_summary_done():
    assert Task(title="Buy milk", priority=2, id=3, done=True).summary() == "[x] #3 Buy milk (P2)"


def test_summary_with_due_date():
    task = Task(title="Pay rent", priority=1, id=7, due_date=date(2026, 10, 1))
    assert task.summary() == "[ ] #7 Pay rent (P1, due 2026-10-01)"


def test_summary_done_with_due_date():
    task = Task(title="Pay rent", priority=1, id=7, due_date=date(2026, 10, 1), done=True)
    assert task.summary() == "[x] #7 Pay rent (P1, due 2026-10-01)"
