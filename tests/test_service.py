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
