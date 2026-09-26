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


def test_search_matches_title_substring_ignoring_case(repo):
    repo.add(Task(title="Buy MILK"))
    repo.add(Task(title="Pay rent"))
    repo.add(Task(title="Refill milk jug"))
    assert [t.title for t in repo.search("Milk")] == ["Buy MILK", "Refill milk jug"]


def test_search_matches_non_ascii_titles_ignoring_case(repo):
    repo.add(Task(title="Ärger klären"))
    assert [t.title for t in repo.search("ÄRGER")] == ["Ärger klären"]


def test_search_returns_complete_tasks(repo):
    added = repo.add(Task(title="Pay rent", priority=1, due_date=date(2026, 10, 1), tags=["home"]))
    assert repo.search("rent") == [added]


def test_search_without_match_returns_empty_list(repo):
    repo.add(Task(title="Buy milk"))
    assert repo.search("bread") == []


def test_search_on_empty_board_returns_empty_list(repo):
    assert repo.search("anything") == []


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("10%", ["Raise budget 10%"]),
        ("e_c", ["Rename snake_case vars"]),
        ("c:\tmp", ["Clean C:\tmp"]),
    ],
)
def test_search_matches_like_wildcards_literally(repo, query, expected):
    repo.add(Task(title="Raise budget 10%"))
    repo.add(Task(title="Raise budget 100 dollars"))
    repo.add(Task(title="Rename snake_case vars"))
    repo.add(Task(title="Rename snakeXcase vars"))
    repo.add(Task(title="Clean C:\tmp"))
    repo.add(Task(title="Clean C:tmp"))
    assert [t.title for t in repo.search(query)] == expected


def test_search_filters_by_exact_tag_ignoring_case(repo):
    repo.add(Task(title="Plan sprint", tags=["work"]))
    repo.add(Task(title="Plan trip", tags=["travel"]))
    repo.add(Task(title="Plan workshop", tags=["workshop"]))
    repo.add(Task(title="Plan yearly goals", tags=["Work", "urgent"]))
    result = repo.search("plan", tag="WORK")
    assert [t.title for t in result] == ["Plan sprint", "Plan yearly goals"]


def test_search_tag_filter_skips_untagged_tasks(repo):
    repo.add(Task(title="Plan sprint"))
    assert repo.search("plan", tag="work") == []


def test_search_can_exclude_done_tasks(repo):
    repo.add(Task(title="Write report", done=True))
    repo.add(Task(title="Write tests"))
    assert [t.title for t in repo.search("write")] == ["Write report", "Write tests"]
    assert [t.title for t in repo.search("write", include_done=False)] == ["Write tests"]


def test_search_combines_tag_and_status_filters(repo):
    repo.add(Task(title="Fix login page", tags=["work"], done=True))
    repo.add(Task(title="Fix sink", tags=["home"]))
    repo.add(Task(title="Fix typo in docs", tags=["work"]))
    result = repo.search("fix", tag="work", include_done=False)
    assert [t.title for t in result] == ["Fix typo in docs"]


def test_search_filters_are_keyword_only(repo):
    with pytest.raises(TypeError):
        repo.search("plan", "work")
