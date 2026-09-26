import pytest

from taskboard.service import TaskService
from taskboard.storage import TaskRepository


@pytest.fixture
def repo() -> TaskRepository:
    return TaskRepository()


@pytest.fixture
def service(repo: TaskRepository) -> TaskService:
    return TaskService(repo)
