from datetime import date

from taskboard.formatting import format_task_detail, format_task_table
from taskboard.models import Task


def _sample_tasks() -> list[Task]:
    return [
        Task(title="Pay rent", priority=1, due_date=date(2026, 10, 1), done=True, id=1),
        Task(title="Buy milk", id=2),
    ]


def test_table_of_empty_list():
    assert format_task_table([]) == "(no tasks)"


def test_table_layout():
    assert format_task_table(_sample_tasks()) == "\n".join(
        [
            "ID  Done  Pri  Due         Title",
            "--  ----  ---  ----------  --------",
            " 1  yes   P1   2026-10-01  Pay rent",
            " 2  no    P3   -           Buy milk",
        ]
    )


def test_table_has_header_separator_and_one_row_per_task():
    lines = format_task_table(_sample_tasks()).splitlines()
    assert len(lines) == 2 + 2
    assert lines[0].split() == ["ID", "Done", "Pri", "Due", "Title"]
    assert set(lines[1].replace(" ", "")) == {"-"}


def test_table_single_task_columns_fit_headers():
    table = format_task_table([Task(title="A", priority=5, id=4)])
    assert table.splitlines() == [
        "ID  Done  Pri  Due  Title",
        "--  ----  ---  ---  -----",
        " 4  no    P5   -    A",
    ]


def test_table_columns_widen_to_fit_content():
    tasks = [
        Task(title="Short", id=9),
        Task(title="A much longer title", id=100),
    ]
    lines = format_task_table(tasks).splitlines()
    assert lines[1] == "---  ----  ---  ---  -------------------"
    assert lines[2] == "  9  no    P3   -    Short"
    assert lines[3] == "100  no    P3   -    A much longer title"


def test_table_keeps_input_order():
    tasks = [Task(title="second", id=2), Task(title="first", id=1)]
    rows = format_task_table(tasks).splitlines()[2:]
    assert [row.split()[-1] for row in rows] == ["second", "first"]


def test_table_lines_have_no_trailing_whitespace():
    for line in format_task_table(_sample_tasks()).splitlines():
        assert line == line.rstrip()


def test_table_of_stored_tasks(service):
    service.create_task("Write report", priority=2)
    service.complete_task(service.create_task("Ship it").id)
    table = format_task_table(service.list_tasks())
    assert table.splitlines()[2:] == [
        " 1  no    P2   -    Write report",
        " 2  yes   P3   -    Ship it",
    ]


def test_detail_with_all_fields():
    task = Task(
        title="Pay rent",
        priority=1,
        due_date=date(2026, 10, 1),
        done=True,
        tags=["home", "bills"],
        id=5,
    )
    assert format_task_detail(task) == "\n".join(
        [
            "Task #5: Pay rent",
            "  Status:   done",
            "  Priority: P1",
            "  Due:      2026-10-01",
            "  Tags:     home, bills",
        ]
    )


def test_detail_without_due_date_or_tags():
    assert format_task_detail(Task(title="Buy milk", id=2)).splitlines() == [
        "Task #2: Buy milk",
        "  Status:   open",
        "  Priority: P3",
        "  Due:      -",
        "  Tags:     -",
    ]
