import pytest

from taskboard.models import Task


def test_page_size_respected(repo):
    for i in range(5):
        repo.add(Task(title=f"task {i}"))
    assert len(repo.list_page(1, 2)) == 2


def test_invalid_page_rejected(repo):
    with pytest.raises(ValueError):
        repo.list_page(0, 2)
