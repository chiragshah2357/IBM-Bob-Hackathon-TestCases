import sqlite3
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


def test_delete_removes_only_that_task(repo):
    keep = repo.add(Task(title="keep"))
    gone = repo.add(Task(title="gone"))
    repo.delete(gone.id)
    assert repo.list_all() == [keep]
    with pytest.raises(TaskNotFoundError):
        repo.get(gone.id)


def test_deleted_id_is_not_reused(repo):
    first = repo.add(Task(title="first"))
    repo.delete(first.id)
    second = repo.add(Task(title="second"))
    assert second.id > first.id


def test_count_empty_board_is_zero(repo):
    assert repo.count() == 0


def test_count_tracks_adds_and_deletes(repo):
    tasks = [repo.add(Task(title=f"task {i}")) for i in range(3)]
    assert repo.count() == 3
    repo.delete(tasks[1].id)
    assert repo.count() == 2


def test_count_includes_done_tasks(repo):
    repo.add(Task(title="open"))
    repo.add(Task(title="finished", done=True))
    assert repo.count() == 2


def test_delete_completed_removes_only_done_tasks(repo):
    open_task = repo.add(Task(title="open"))
    repo.add(Task(title="done 1", done=True))
    repo.add(Task(title="done 2", done=True))
    assert repo.delete_completed() == 2
    assert repo.list_all() == [open_task]


def test_delete_completed_without_done_tasks_returns_zero(repo):
    repo.add(Task(title="open"))
    assert repo.delete_completed() == 0
    assert repo.count() == 1


def test_delete_completed_on_empty_board_returns_zero(repo):
    assert repo.delete_completed() == 0


def test_failed_delete_is_rolled_back_and_reraised(tmp_path):
    path = str(tmp_path / "board.db")
    repo = TaskRepository(path)
    task = repo.add(Task(title="protected"))
    other = sqlite3.connect(path, timeout=0)
    other.execute(
        "CREATE TRIGGER block_delete BEFORE DELETE ON tasks "
        "BEGIN SELECT RAISE(ABORT, 'deletes are blocked'); END"
    )
    other.commit()

    with pytest.raises(sqlite3.IntegrityError):
        repo.delete(task.id)

    # Only succeeds if the repository released its write transaction.
    other.execute("DROP TRIGGER block_delete")
    other.commit()
    other.close()
    assert repo.get(task.id) == task
    repo.delete(task.id)
    assert repo.count() == 0
