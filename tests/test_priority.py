from datetime import date

import pytest

from taskboard.models import MIN_PRIORITY
from taskboard.storage import TaskNotFoundError


def test_create_task_defaults_to_priority_three(service):
    assert service.create_task("Water plants").priority == 3


def test_create_task_accepts_highest_priority(service):
    task = service.create_task("Fix outage", priority=1)
    assert task.priority == 1
    assert service.list_tasks()[0].priority == 1


@pytest.mark.parametrize("priority", [2, 3, 4])
def test_create_task_accepts_middle_priorities(service, priority):
    assert service.create_task("Tidy desk", priority=priority).priority == priority


@pytest.mark.parametrize("priority", [0, 6, -1, 100])
def test_create_task_rejects_out_of_range_priority(service, priority):
    with pytest.raises(ValueError):
        service.create_task("Tidy desk", priority=priority)
    assert service.list_tasks() == []


@pytest.mark.parametrize("priority", ["2", 2.0, None, True])
def test_create_task_rejects_non_integer_priority(service, priority):
    with pytest.raises(ValueError):
        service.create_task("Tidy desk", priority=priority)
    assert service.list_tasks() == []


def test_set_priority_updates_and_persists(service):
    task = service.create_task("Renew passport", priority=3)
    updated = service.set_priority(task.id, 2)
    assert updated.priority == 2
    assert service.list_tasks()[0].priority == 2


def test_set_priority_accepts_highest_priority(service):
    task = service.create_task("Renew passport", priority=4)
    assert service.set_priority(task.id, 1).priority == 1
    assert service.list_tasks()[0].priority == 1


def test_set_priority_keeps_other_fields(service):
    task = service.create_task(
        "Renew passport", priority=3, due_date=date(2026, 11, 2), tags=["admin"]
    )
    service.set_priority(task.id, 1)
    stored = service.list_tasks()[0]
    assert stored.title == "Renew passport"
    assert stored.due_date == date(2026, 11, 2)
    assert stored.tags == ["admin"]
    assert stored.done is False


def test_set_priority_same_value_returns_task_unchanged(service):
    task = service.create_task("Renew passport", priority=2)
    assert service.set_priority(task.id, 2) == task
    assert service.list_tasks()[0].priority == 2


@pytest.mark.parametrize("priority", [0, 6, -1])
def test_set_priority_rejects_out_of_range_priority(service, priority):
    task = service.create_task("Renew passport", priority=2)
    with pytest.raises(ValueError):
        service.set_priority(task.id, priority)
    assert service.list_tasks()[0].priority == 2


def test_set_priority_rejects_non_integer_priority(service):
    task = service.create_task("Renew passport", priority=2)
    with pytest.raises(ValueError):
        service.set_priority(task.id, "1")
    assert service.list_tasks()[0].priority == 2


def test_set_priority_missing_id_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.set_priority(99, 2)


def test_bump_priority_makes_task_more_urgent(service):
    task = service.create_task("Call dentist", priority=4)
    assert service.bump_priority(task.id).priority == 3
    assert service.list_tasks()[0].priority == 3


def test_bump_priority_never_goes_below_highest(service):
    task = service.create_task("Call dentist", priority=2)
    assert service.bump_priority(task.id).priority == MIN_PRIORITY
    assert service.bump_priority(task.id).priority == MIN_PRIORITY
    assert service.list_tasks()[0].priority == MIN_PRIORITY


def test_bump_priority_missing_id_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.bump_priority(99)


def test_list_by_priority_orders_by_priority_then_id(service):
    a = service.create_task("a", priority=3)
    b = service.create_task("b", priority=1)
    c = service.create_task("c", priority=3)
    d = service.create_task("d", priority=2)
    assert [t.id for t in service.list_by_priority()] == [b.id, d.id, a.id, c.id]


def test_list_by_priority_excludes_done_tasks(service):
    open_task = service.create_task("open", priority=2)
    done_task = service.create_task("done", priority=1)
    service.complete_task(done_task.id)
    assert [t.id for t in service.list_by_priority()] == [open_task.id]


def test_list_by_priority_reflects_priority_changes(service):
    first = service.create_task("first", priority=2)
    second = service.create_task("second", priority=4)
    service.set_priority(second.id, 1)
    assert [t.id for t in service.list_by_priority()] == [second.id, first.id]


def test_list_by_priority_empty_board(service):
    assert service.list_by_priority() == []
