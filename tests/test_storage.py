from datetime import date

import pytest

from taskboard.models import Task
from taskboard.storage import TaskNotFoundError, TaskRepository


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


def add_tasks(repo: TaskRepository, n: int) -> None:
    for i in range(n):
        repo.add(Task(title=f"task {i}"))


def test_count_empty_repo(repo):
    assert repo.count() == 0


def test_count_after_adds(repo):
    add_tasks(repo, 3)
    assert repo.count() == 3


def test_list_page_reports_metadata(repo):
    add_tasks(repo, 5)
    page = repo.list_page(1, 2)
    assert page.page == 1
    assert page.page_size == 2
    assert page.total == 5
    assert page.total_pages == 3
    assert page.has_next is True


def test_list_page_first_page_is_full(repo):
    add_tasks(repo, 5)
    page = repo.list_page(1, 2)
    assert len(page.items) == 2
    assert all(isinstance(t, Task) for t in page.items)
    ids = [t.id for t in page.items]
    assert ids == sorted(ids)


def test_list_page_past_the_end_is_empty(repo):
    add_tasks(repo, 5)
    page = repo.list_page(10, 2)
    assert page.items == []
    assert page.total == 5
    assert page.has_next is False


def test_list_page_empty_repo(repo):
    page = repo.list_page(1, 20)
    assert page.items == []
    assert page.total == 0
    assert page.total_pages == 0
    assert page.has_next is False


@pytest.mark.parametrize("page_number", [0, -1])
def test_list_page_rejects_page_below_one(repo, page_number):
    with pytest.raises(ValueError):
        repo.list_page(page_number, 10)


@pytest.mark.parametrize("page_size", [0, -3])
def test_list_page_rejects_page_size_below_one(repo, page_size):
    with pytest.raises(ValueError):
        repo.list_page(1, page_size)
