from datetime import date

import pytest

from taskboard.storage import TaskNotFoundError
from taskboard.utils import parse_date

TODAY = date(2026, 9, 26)


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


def test_set_due_date_iso_persists(service, repo):
    task = service.create_task("Pay rent")
    updated = service.set_due_date(task.id, "2026-10-01", today=TODAY)
    assert updated.due_date == date(2026, 10, 1)
    assert repo.get(task.id).due_date == date(2026, 10, 1)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("today", TODAY),
        ("Tomorrow", date(2026, 9, 27)),
        (" +3D ", date(2026, 9, 29)),
    ],
)
def test_set_due_date_relative_uses_today(service, repo, value, expected):
    task = service.create_task("Water plants")
    assert service.set_due_date(task.id, value, today=TODAY).due_date == expected
    assert repo.get(task.id).due_date == expected


def test_set_due_date_replaces_existing_date(service, repo):
    task = service.create_task("Renew passport", due_date=date(2026, 12, 1))
    service.set_due_date(task.id, "+7d", today=TODAY)
    assert repo.get(task.id).due_date == date(2026, 10, 3)


def test_set_due_date_keeps_other_fields(service, repo):
    task = service.create_task("Book flights", priority=1, tags=["travel"])
    service.set_due_date(task.id, "tomorrow", today=TODAY)
    stored = repo.get(task.id)
    assert (stored.title, stored.priority, stored.tags, stored.done) == (
        "Book flights",
        1,
        ["travel"],
        False,
    )


def test_set_due_date_defaults_today_to_current_date(service):
    task = service.create_task("Call bank")
    before = date.today()
    updated = service.set_due_date(task.id, "today")
    assert updated.due_date in (before, date.today())


def test_set_due_date_invalid_value_leaves_task_unchanged(service, repo):
    task = service.create_task("File taxes", due_date=date(2026, 11, 15))
    with pytest.raises(ValueError):
        service.set_due_date(task.id, "next friday", today=TODAY)
    assert repo.get(task.id).due_date == date(2026, 11, 15)


def test_set_due_date_missing_id_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.set_due_date(99, "tomorrow", today=TODAY)


def test_set_due_date_missing_id_does_not_create_task(service):
    with pytest.raises(TaskNotFoundError):
        service.set_due_date(1, "2026-10-01", today=TODAY)
    assert service.list_tasks() == []
