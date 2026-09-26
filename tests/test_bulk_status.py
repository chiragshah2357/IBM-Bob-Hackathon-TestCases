import pytest

from taskboard.models import Task
from taskboard.storage import TaskNotFoundError


def _done_flags(service):
    return [task.done for task in service.list_tasks()]


# --- completeAllWithTag -------------------------------------------------------


def test_complete_all_with_tag_completes_matching_open_tasks(service):
    service.create_task("Write tests", tags=["sprint"])
    service.create_task("Fix login", tags=["sprint", "ui"])
    service.create_task("Plan offsite", tags=["backlog"])

    assert service.completeAllWithTag("sprint") == 2
    assert _done_flags(service) == [True, True, False]


@pytest.mark.parametrize("tag", ["Sprint", "SPRINT", "  sprint  "])
def test_complete_all_with_tag_is_case_insensitive(service, tag):
    service.create_task("Write tests", tags=["sprint"])

    assert service.completeAllWithTag(tag) == 1
    assert _done_flags(service) == [True]


def test_complete_all_with_tag_matches_mixed_case_stored_tags(service, repo):
    repo.add(Task(title="Imported task", tags=["Sprint"]))

    assert service.completeAllWithTag("sprint") == 1
    assert _done_flags(service) == [True]


def test_complete_all_with_tag_does_not_count_done_tasks(service):
    first = service.create_task("Write tests", tags=["sprint"])
    service.create_task("Fix login", tags=["sprint"])
    service.complete_task(first.id)

    assert service.completeAllWithTag("sprint") == 1
    assert service.completeAllWithTag("sprint") == 0
    assert _done_flags(service) == [True, True]


def test_complete_all_with_tag_requires_exact_tag(service):
    service.create_task("Next sprint", tags=["sprint-2"])

    assert service.completeAllWithTag("sprint") == 0
    assert _done_flags(service) == [False]


def test_complete_all_with_tag_on_empty_board_returns_zero(service):
    assert service.completeAllWithTag("sprint") == 0


def test_complete_all_with_tag_persists_changes(service, repo):
    task = service.create_task("Write tests", tags=["sprint"])

    service.completeAllWithTag("sprint")

    assert repo.get(task.id).done is True


@pytest.mark.parametrize("tag", ["", "   "])
def test_complete_all_with_tag_rejects_blank_tag(service, tag):
    service.create_task("Write tests", tags=["sprint"])

    with pytest.raises(ValueError):
        service.completeAllWithTag(tag)
    assert _done_flags(service) == [False]


# --- complete_many ------------------------------------------------------------


def test_complete_many_completes_listed_tasks(service):
    a = service.create_task("a")
    service.create_task("b")
    c = service.create_task("c")

    assert service.complete_many([a.id, c.id]) == 2
    assert _done_flags(service) == [True, False, True]


def test_complete_many_does_not_count_done_tasks(service):
    a = service.create_task("a")
    b = service.create_task("b")
    service.complete_task(a.id)

    assert service.complete_many([a.id, b.id]) == 1
    assert _done_flags(service) == [True, True]


def test_complete_many_counts_repeated_ids_once(service):
    a = service.create_task("a")

    assert service.complete_many([a.id, a.id, a.id]) == 1
    assert _done_flags(service) == [True]


def test_complete_many_with_no_ids_changes_nothing(service):
    service.create_task("a")

    assert service.complete_many([]) == 0
    assert _done_flags(service) == [False]


def test_complete_many_missing_id_changes_nothing(service):
    a = service.create_task("a")
    b = service.create_task("b")

    with pytest.raises(TaskNotFoundError):
        service.complete_many([a.id, 99, b.id])
    assert _done_flags(service) == [False, False]


def test_complete_many_reports_every_missing_id(service):
    a = service.create_task("a")

    with pytest.raises(TaskNotFoundError, match=r"\[98, 99\]"):
        service.complete_many([98, a.id, 99])


@pytest.mark.parametrize("bad_id", ["1", 1.0, True, None])
def test_complete_many_rejects_non_integer_ids(service, bad_id):
    a = service.create_task("a")

    with pytest.raises(ValueError):
        service.complete_many([a.id, bad_id])
    assert _done_flags(service) == [False]


# --- reopen_task --------------------------------------------------------------


def test_reopen_task_marks_task_open(service, repo):
    task = service.create_task("a")
    service.complete_task(task.id)

    reopened = service.reopen_task(task.id)

    assert reopened.done is False
    assert repo.get(task.id).done is False


def test_reopen_open_task_is_a_no_op(service):
    task = service.create_task("a")

    assert service.reopen_task(task.id) == task
    assert _done_flags(service) == [False]


def test_reopen_task_missing_id_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.reopen_task(42)


def test_reopened_task_is_completed_again_by_tag(service):
    a = service.create_task("a", tags=["sprint"])
    service.create_task("b", tags=["sprint"])
    service.completeAllWithTag("sprint")

    service.reopen_task(a.id)

    assert service.completeAllWithTag("sprint") == 1
    assert _done_flags(service) == [True, True]
