from datetime import date


def test_past_due_task_is_overdue(service):
    service.create_task("File taxes", due_date=date(2026, 9, 20))
    overdue = service.list_overdue(date(2026, 9, 26))
    assert [t.title for t in overdue] == ["File taxes"]


def test_task_without_due_date_is_not_overdue(service):
    service.create_task("Someday")
    assert service.list_overdue(date(2026, 9, 26)) == []
