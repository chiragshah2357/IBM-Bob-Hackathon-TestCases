import logging
from datetime import date

import pytest

from taskboard.storage import TaskNotFoundError
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


def test_describe_returns_multiline_detail(service):
    task = service.create_task("Pay rent", priority=1, due_date=date(2026, 10, 1), tags=["home"])
    assert service.describe(task.id) == "\n".join(
        [
            f"Task #{task.id}: Pay rent",
            "  Status:   open",
            "  Priority: P1",
            "  Due:      2026-10-01",
            "  Tags:     home",
        ]
    )


def test_describe_reflects_completion(service):
    task = service.create_task("Write report")
    service.complete_task(task.id)
    assert "  Status:   done" in service.describe(task.id).splitlines()


def test_describe_picks_the_requested_task(service):
    service.create_task("First")
    second = service.create_task("Second")
    assert service.describe(second.id).splitlines()[0] == f"Task #{second.id}: Second"


def test_describe_missing_id_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.describe(99)


def test_describe_missing_id_on_non_empty_board_raises(service, caplog):
    service.create_task("Only task")
    with caplog.at_level(logging.WARNING, logger="taskboard.service"):
        with pytest.raises(TaskNotFoundError):
            service.describe(2)
    assert "cannot describe task 2" in caplog.text
