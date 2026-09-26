import pytest

from taskboard.service import TaskService
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


def create_tasks(service: TaskService, n: int) -> None:
    for i in range(n):
        service.create_task(f"task {i}")


def test_list_tasks_page_defaults(service):
    create_tasks(service, 45)
    page = service.list_tasks_page()
    assert page.page == 1
    assert page.page_size == 20
    assert len(page.items) == 20
    assert page.total == 45
    assert page.total_pages == 3
    assert page.has_next is True


def test_list_tasks_page_custom_size(service):
    create_tasks(service, 6)
    page = service.list_tasks_page(page=1, page_size=3)
    assert len(page.items) == 3
    assert page.total_pages == 2
    assert page.has_next is True


def test_list_tasks_page_past_the_end_is_empty(service):
    create_tasks(service, 6)
    page = service.list_tasks_page(page=3, page_size=3)
    assert page.items == []
    assert page.total == 6
    assert page.has_next is False


def test_list_tasks_page_empty_board(service):
    page = service.list_tasks_page()
    assert page.items == []
    assert page.total == 0
    assert page.has_next is False


def test_list_tasks_page_rejects_page_zero(service):
    with pytest.raises(ValueError):
        service.list_tasks_page(page=0)


def test_list_tasks_page_rejects_page_size_zero(service):
    with pytest.raises(ValueError):
        service.list_tasks_page(page_size=0)
