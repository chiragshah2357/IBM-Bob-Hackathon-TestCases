import logging

import pytest

from taskboard.utils import parse_date


def test_create_task_strips_title(service):
    task = service.create_task("  Buy milk  ")
    assert task.title == "Buy milk"


def test_create_task_rejects_blank_title(service):
    with pytest.raises(ValueError):
        service.create_task("   ")


def test_complete_task_marks_done(service):
    task = service.create_task("Write report")
    assert service.complete_task(task.id).done is True
    assert service.list_tasks()[0].done is True


def test_parse_date_iso():
    assert parse_date("2026-10-01").isoformat() == "2026-10-01"


def test_parse_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_date("next week")


def test_delete_task_removes_task(service):
    keep = service.create_task("Keep")
    gone = service.create_task("Gone")
    assert service.delete_task(gone.id) is None
    assert service.list_tasks() == [keep]


def test_delete_task_logs_deletion(service, caplog):
    task = service.create_task("Old note")
    with caplog.at_level(logging.INFO, logger="taskboard.service"):
        service.delete_task(task.id)
    assert f"deleted task {task.id}" in caplog.text


@pytest.mark.parametrize("bad_id", ["1", 1.0, None, True])
def test_delete_task_rejects_non_int_id(service, bad_id):
    task = service.create_task("Survivor")
    with pytest.raises(ValueError):
        service.delete_task(bad_id)
    assert service.list_tasks() == [task]


def test_delete_completed_returns_number_removed(service):
    first = service.create_task("Laundry")
    service.create_task("Taxes")
    third = service.create_task("Groceries")
    service.complete_task(first.id)
    service.complete_task(third.id)
    assert service.delete_completed() == 2
    assert [t.title for t in service.list_tasks()] == ["Taxes"]


def test_delete_completed_twice_removes_nothing_the_second_time(service):
    task = service.create_task("Done already")
    service.complete_task(task.id)
    assert service.delete_completed() == 1
    assert service.delete_completed() == 0


def test_delete_completed_keeps_open_tasks(service):
    service.create_task("Open 1")
    service.create_task("Open 2")
    assert service.delete_completed() == 0
    assert [t.title for t in service.list_tasks()] == ["Open 1", "Open 2"]


def test_delete_completed_on_empty_board(service):
    assert service.delete_completed() == 0
    assert service.list_tasks() == []
