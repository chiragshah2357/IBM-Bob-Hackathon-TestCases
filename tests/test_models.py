from datetime import date

import pytest

from taskboard.models import MAX_PRIORITY, MIN_PRIORITY, Task


def test_summary_open_task_without_due_date():
    task = Task(title="Buy milk", id=1)
    assert task.summary() == "[ ] #1 Buy milk (P3)"


def test_summary_done_task():
    task = Task(title="Pay rent", priority=1, done=True, id=7)
    assert task.summary() == "[x] #7 Pay rent (P1)"


def test_summary_includes_due_date():
    task = Task(title="File taxes", priority=2, due_date=date(2026, 10, 1), id=3)
    assert task.summary() == "[ ] #3 File taxes (P2, due 2026-10-01)"


def test_summary_done_task_with_due_date():
    task = Task(title="File taxes", priority=2, due_date=date(2026, 10, 1), done=True, id=3)
    assert task.summary() == "[x] #3 File taxes (P2, due 2026-10-01)"


@pytest.mark.parametrize("priority", [MIN_PRIORITY, MAX_PRIORITY])
def test_summary_priority_boundaries(priority):
    task = Task(title="Edge", priority=priority, id=1)
    assert task.summary() == f"[ ] #1 Edge (P{priority})"


def test_summary_does_not_include_tags():
    task = Task(title="Call mum", tags=["family"], id=2)
    assert task.summary() == "[ ] #2 Call mum (P3)"


def test_summary_of_unsaved_task_uses_placeholder_id():
    assert Task(title="Draft").summary() == "[ ] #? Draft (P3)"


def test_id_label():
    assert Task(title="a", id=12).id_label == "12"
    assert Task(title="a").id_label == "?"


def test_summary_uses_id_assigned_by_storage(service):
    service.create_task("First")
    task = service.create_task("Second", priority=4)
    assert task.summary() == "[ ] #2 Second (P4)"
