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


def test_update_many_persists_every_task(repo):
    a = repo.add(Task(title="a"))
    b = repo.add(Task(title="b"))
    a.done = True
    b.priority = 1

    repo.update_many([a, b])

    assert repo.get(a.id).done is True
    assert repo.get(b.id).priority == 1


def test_update_many_missing_id_rolls_back(repo):
    a = repo.add(Task(title="a"))
    a.done = True

    with pytest.raises(TaskNotFoundError):
        repo.update_many([a, Task(title="ghost", id=42)])
    assert repo.get(a.id).done is False


def test_update_many_with_no_tasks_is_a_no_op(repo):
    repo.add(Task(title="a"))

    repo.update_many([])

    assert [t.done for t in repo.list_all()] == [False]
