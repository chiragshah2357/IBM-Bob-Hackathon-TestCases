import pytest

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


def test_search_tasks_strips_query(service):
    service.create_task("Buy milk")
    service.create_task("Pay rent")
    assert [t.title for t in service.search_tasks("  MILK  ")] == ["Buy milk"]


@pytest.mark.parametrize("query", ["", "   ", "\t\n"])
def test_search_tasks_rejects_blank_query(service, query):
    with pytest.raises(ValueError):
        service.search_tasks(query)


def test_search_tasks_applies_tag_and_status_filters(service):
    report = service.create_task("Draft report", tags=["work"])
    service.complete_task(report.id)
    service.create_task("Draft speech", tags=["work"])
    service.create_task("Draft shopping list", tags=["home"])
    all_work = service.search_tasks("draft", tag="WORK")
    assert [t.title for t in all_work] == ["Draft report", "Draft speech"]
    open_work = service.search_tasks("draft", tag="work", include_done=False)
    assert [t.title for t in open_work] == ["Draft speech"]


def test_search_tasks_without_match_returns_empty_list(service):
    service.create_task("Buy milk")
    assert service.search_tasks("bread") == []
