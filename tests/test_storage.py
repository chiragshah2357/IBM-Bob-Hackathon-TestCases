from datetime import date

import pytest

from taskboard.models import Task
from taskboard.storage import TaskNotFoundError


def test_add_assigns_id(repo):
    task = repo.add(Task(title="Buy milk"))
    assert task.id == 1


def test_get_round_trips_all_fields(repo):
    added = repo.add(Task(title="Pay rent", priority=1, due_date=date(2026, 10, 1), tags=["home"]))
    fetched = repo.get(added.id)
    assert fetched == added


def test_get_missing_raises(repo):
    with pytest.raises(TaskNotFoundError):
        repo.get(99)


def test_update_missing_raises(repo):
    with pytest.raises(TaskNotFoundError):
        repo.update(Task(title="ghost", id=42))


def test_list_all_orders_by_id(repo):
    repo.add(Task(title="a"))
    repo.add(Task(title="b"))
    assert [t.title for t in repo.list_all()] == ["a", "b"]


def test_update_priority_changes_only_priority(repo):
    added = repo.add(Task(title="Pay rent", priority=3, due_date=date(2026, 10, 1), tags=["home"]))
    repo.update_priority(added.id, 1)
    fetched = repo.get(added.id)
    assert fetched.priority == 1
    assert fetched.title == "Pay rent"
    assert fetched.due_date == date(2026, 10, 1)
    assert fetched.tags == ["home"]


def test_update_priority_missing_raises(repo):
    with pytest.raises(TaskNotFoundError):
        repo.update_priority(42, 2)


def test_list_open_by_priority_orders_and_skips_done(repo):
    repo.add(Task(title="low", priority=4))
    repo.add(Task(title="finished", priority=1, done=True))
    repo.add(Task(title="urgent", priority=1))
    repo.add(Task(title="also low", priority=4))
    assert [t.title for t in repo.list_open_by_priority()] == ["urgent", "low", "also low"]


def test_list_open_by_priority_empty(repo):
    assert repo.list_open_by_priority() == []
