import pytest

from taskboard.storage import TaskNotFoundError
from taskboard.utils import normalize_tag, normalize_tags


def test_normalize_tag_strips_and_lowercases():
    assert normalize_tag("  Work ") == "work"


def test_normalize_tag_keeps_inner_spaces():
    assert normalize_tag(" Big Project ") == "big project"


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_normalize_tag_rejects_blank(blank):
    with pytest.raises(ValueError):
        normalize_tag(blank)


def test_normalize_tags_drops_duplicates_keeping_first_seen_order():
    assert normalize_tags(["Home", "work", "HOME", " work "]) == ["home", "work"]


def test_normalize_tags_empty_input():
    assert normalize_tags([]) == []


def test_normalize_tags_names_position_of_blank_tag():
    with pytest.raises(ValueError, match="position 1"):
        normalize_tags(["home", "   "])


def test_create_task_normalizes_and_dedupes_tags(service):
    task = service.create_task("Plan trip", tags=[" Travel", "HOME", "travel"])
    assert task.tags == ["travel", "home"]
    assert service.list_tasks()[0].tags == ["travel", "home"]


def test_create_task_without_tags_has_no_tags(service):
    assert service.create_task("Plan trip").tags == []


def test_create_task_rejects_blank_tag(service):
    with pytest.raises(ValueError):
        service.create_task("Plan trip", tags=["home", " "])
    assert service.list_tasks() == []


def test_add_tag_normalizes_and_persists(service, repo):
    task = service.create_task("Pay rent")
    updated = service.add_tag(task.id, "  Urgent ")
    assert updated.tags == ["urgent"]
    assert repo.get(task.id).tags == ["urgent"]


def test_add_tag_appends_after_existing_tags(service, repo):
    task = service.create_task("Pay rent", tags=["home"])
    service.add_tag(task.id, "money")
    assert repo.get(task.id).tags == ["home", "money"]


def test_add_existing_tag_is_noop(service, repo):
    task = service.create_task("Pay rent", tags=["home"])
    assert service.add_tag(task.id, "home").tags == ["home"]
    assert repo.get(task.id).tags == ["home"]


def test_add_tag_rejects_blank_and_leaves_task_unchanged(service, repo):
    task = service.create_task("Pay rent", tags=["home"])
    with pytest.raises(ValueError):
        service.add_tag(task.id, "   ")
    assert repo.get(task.id).tags == ["home"]


def test_add_tag_missing_task_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.add_tag(99, "home")


def test_remove_tag_removes_and_persists(service, repo):
    task = service.create_task("Pay rent", tags=["home", "money"])
    assert service.remove_tag(task.id, "home").tags == ["money"]
    assert repo.get(task.id).tags == ["money"]


def test_remove_last_tag_leaves_empty_list(service, repo):
    task = service.create_task("Pay rent", tags=["home"])
    service.remove_tag(task.id, "home")
    assert repo.get(task.id).tags == []


def test_remove_absent_tag_is_noop(service, repo):
    task = service.create_task("Pay rent", tags=["home"])
    assert service.remove_tag(task.id, "work").tags == ["home"]
    assert repo.get(task.id).tags == ["home"]


def test_remove_tag_missing_task_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.remove_tag(99, "home")


def test_list_tags_empty_board(service):
    assert service.list_tags() == []


def test_list_tags_distinct_and_sorted(service):
    service.create_task("a", tags=["work", "home"])
    service.create_task("b", tags=["home", "errands"])
    service.create_task("c")
    assert service.list_tags() == ["errands", "home", "work"]


def test_tasks_with_tag_is_case_insensitive_and_ordered_by_id(service):
    first = service.create_task("a", tags=["work"])
    service.create_task("b", tags=["home"])
    third = service.create_task("c", tags=["urgent", "work"])
    assert [t.id for t in service.tasks_with_tag(" WORK ")] == [first.id, third.id]


def test_tasks_with_tag_no_match_returns_empty(service):
    service.create_task("a", tags=["work"])
    assert service.tasks_with_tag("travel") == []


def test_tasks_with_tag_rejects_blank(service):
    with pytest.raises(ValueError):
        service.tasks_with_tag("  ")
