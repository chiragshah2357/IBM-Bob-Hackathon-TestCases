import logging

import pytest

from taskboard.models import Task
from taskboard.service import TaskService
from taskboard.stats import BoardStats, format_stats


def _priorities(**counts: int) -> dict[int, int]:
    """Build a full 1-5 priority map; pass e.g. p1=2 to set a count."""
    return {priority: counts.get(f"p{priority}", 0) for priority in range(1, 6)}


def _add(service: TaskService, title: str, *, priority: int = 3, done: bool = False) -> None:
    task = service.create_task(title, priority=priority)
    if done:
        service.complete_task(task.id)


def test_completion_rate_all_done(service):
    _add(service, "a", done=True)
    _add(service, "b", done=True)
    assert service.completion_rate() == 100.0


def test_completion_rate_none_done(service):
    _add(service, "a")
    _add(service, "b")
    assert service.completion_rate() == 0.0


def test_completion_rate_rounds_down_to_one_decimal(service):
    _add(service, "a", done=True)
    _add(service, "b")
    _add(service, "c")
    assert service.completion_rate() == 33.3


def test_completion_rate_rounds_up_to_one_decimal(service):
    _add(service, "a", done=True)
    _add(service, "b", done=True)
    _add(service, "c")
    assert service.completion_rate() == 66.7


def test_completion_rate_is_float(service):
    _add(service, "a", done=True)
    assert isinstance(service.completion_rate(), float)


def test_stats_summarises_board(service):
    _add(service, "urgent", priority=1)
    _add(service, "also urgent", priority=1)
    _add(service, "normal", priority=3, done=True)
    _add(service, "someday", priority=5)
    assert service.stats() == BoardStats(
        total=4, done=1, open=3, completion_rate=25.0, by_priority=_priorities(p1=2, p5=1)
    )


def test_stats_by_priority_lists_every_priority(service):
    _add(service, "only one", priority=2)
    assert service.stats().by_priority == {1: 0, 2: 1, 3: 0, 4: 0, 5: 0}


def test_stats_by_priority_counts_only_open_tasks(service):
    _add(service, "finished", priority=1, done=True)
    _add(service, "pending", priority=4)
    assert service.stats().by_priority == _priorities(p4=1)


def test_stats_all_done(service):
    _add(service, "a", priority=1, done=True)
    _add(service, "b", priority=5, done=True)
    stats = service.stats()
    assert (stats.total, stats.done, stats.open) == (2, 2, 0)
    assert stats.completion_rate == 100.0
    assert stats.by_priority == _priorities()


def test_stats_agrees_with_completion_rate(service):
    for index in range(7):
        _add(service, f"task {index}", done=index % 3 == 0)
    assert service.stats().completion_rate == service.completion_rate() == 42.9


def test_stats_skips_out_of_range_priority_with_warning(service, repo, caplog):
    repo.add(Task(title="legacy", priority=9))
    _add(service, "valid", priority=2)
    with caplog.at_level(logging.WARNING, logger="taskboard.service"):
        stats = service.stats()
    assert stats.open == 2
    assert stats.by_priority == _priorities(p2=1)
    assert "priority 9" in caplog.text


def test_board_stats_accepts_consistent_numbers():
    stats = BoardStats(
        total=3, done=1, open=2, completion_rate=33.3, by_priority=_priorities(p3=2)
    )
    assert stats.open == 2


@pytest.mark.parametrize(
    "total, done, open_, rate",
    [
        (3, 1, 1, 33.3),  # done + open != total
        (1, -1, 2, 0.0),  # negative count
        (2, 1, 1, -0.1),  # rate below 0
        (2, 1, 1, 100.1),  # rate above 100
    ],
)
def test_board_stats_rejects_inconsistent_numbers(total, done, open_, rate):
    with pytest.raises(ValueError):
        BoardStats(
            total=total, done=done, open=open_, completion_rate=rate, by_priority=_priorities()
        )


@pytest.mark.parametrize(
    "by_priority",
    [
        {1: 0, 2: 0, 3: 0, 4: 0},
        {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        {1: 0, 2: -1, 3: 0, 4: 0, 5: 0},
    ],
)
def test_board_stats_rejects_bad_priority_counts(by_priority):
    with pytest.raises(ValueError):
        BoardStats(total=1, done=1, open=0, completion_rate=100.0, by_priority=by_priority)


def test_format_stats_full_summary():
    stats = BoardStats(
        total=5, done=2, open=3, completion_rate=40.0, by_priority=_priorities(p1=1, p3=2)
    )
    assert format_stats(stats) == "\n".join(
        [
            "Tasks: 5 total, 2 done, 3 open",
            "Completion: 40.0%",
            "Open tasks by priority:",
            "  P1 (highest): 1",
            "  P2: 0",
            "  P3: 2",
            "  P4: 0",
            "  P5 (lowest): 0",
        ]
    )


def test_format_stats_shows_one_decimal():
    stats = BoardStats(
        total=3, done=2, open=1, completion_rate=66.7, by_priority=_priorities(p2=1)
    )
    assert "Completion: 66.7%" in format_stats(stats)


def test_format_stats_from_service(service):
    _add(service, "ship it", priority=2, done=True)
    _add(service, "write docs", priority=4)
    lines = format_stats(service.stats()).splitlines()
    assert lines[0] == "Tasks: 2 total, 1 done, 1 open"
    assert lines[1] == "Completion: 50.0%"
    assert "  P4: 1" in lines
