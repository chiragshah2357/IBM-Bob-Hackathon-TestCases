import csv
import json
import logging
from datetime import date

import pytest

from taskboard.export import CSV_HEADER, export_csv, export_json, task_to_dict
from taskboard.models import Task


@pytest.fixture
def tasks(repo):
    repo.add(Task(title="Pay rent", priority=1, due_date=date(2026, 10, 1), tags=["home", "bills"]))
    repo.add(Task(title="Water plants", done=True))
    repo.add(Task(title="Book dentist", priority=4, tags=["health"]))
    return repo.list_all()


def read_csv_rows(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def test_task_to_dict_uses_iso_date():
    task = Task(title="Pay rent", priority=1, due_date=date(2026, 10, 1), tags=["home"], id=7)
    assert task_to_dict(task) == {
        "id": 7,
        "title": "Pay rent",
        "priority": 1,
        "due_date": "2026-10-01",
        "done": False,
        "tags": ["home"],
    }


def test_task_to_dict_without_due_date_is_none():
    assert task_to_dict(Task(title="Someday"))["due_date"] is None


def test_task_to_dict_copies_tags():
    task = Task(title="Pay rent", tags=["home"])
    task_to_dict(task)["tags"].append("bills")
    assert task.tags == ["home"]


def test_export_csv_writes_header(tmp_path):
    target = tmp_path / "tasks.csv"
    export_csv([Task(title="Buy milk", id=1)], str(target))
    first_line = target.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == "id,title,priority,due_date,done,tags"
    assert read_csv_rows(target)[0] == list(CSV_HEADER)


def test_export_csv_writes_one_row_per_task(tasks, tmp_path):
    target = tmp_path / "tasks.csv"
    assert export_csv(tasks, str(target)) == 3
    rows = read_csv_rows(target)[1:]
    assert rows == [
        ["1", "Pay rent", "1", "2026-10-01", "false", "home;bills"],
        ["2", "Water plants", "3", "", "true", ""],
        ["3", "Book dentist", "4", "", "false", "health"],
    ]


def test_export_csv_rows_parse_with_dict_reader(tasks, tmp_path):
    target = tmp_path / "tasks.csv"
    export_csv(tasks, str(target))
    with open(target, encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert [r["title"] for r in records] == ["Pay rent", "Water plants", "Book dentist"]
    assert records[0]["tags"].split(";") == ["home", "bills"]


def test_export_csv_empty_list_writes_only_header(tmp_path):
    target = tmp_path / "empty.csv"
    assert export_csv([], str(target)) == 0
    assert read_csv_rows(target) == [list(CSV_HEADER)]


def test_export_csv_overwrites_existing_file(tasks, tmp_path):
    target = tmp_path / "tasks.csv"
    export_csv(tasks, str(target))
    assert export_csv(tasks[:1], str(target)) == 1
    assert len(read_csv_rows(target)) == 2


@pytest.mark.parametrize("path", ["", "   "])
def test_export_csv_rejects_blank_path(path):
    with pytest.raises(ValueError):
        export_csv([Task(title="Buy milk")], path)


def test_export_csv_rejects_directory(tmp_path):
    with pytest.raises(ValueError):
        export_csv([Task(title="Buy milk")], str(tmp_path))


def test_export_csv_missing_parent_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_csv([Task(title="Buy milk")], str(tmp_path / "missing" / "tasks.csv"))


def test_export_json_writes_list_of_objects(tasks, tmp_path):
    target = tmp_path / "tasks.json"
    assert export_json(tasks, str(target)) == 3
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data == [task_to_dict(t) for t in tasks]
    assert data[0]["due_date"] == "2026-10-01"


def test_export_json_is_indented_by_two_spaces(tmp_path):
    target = tmp_path / "tasks.json"
    export_json([Task(title="Buy milk", id=1)], str(target))
    lines = target.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "["
    assert lines[1] == "  {"
    assert lines[2] == '    "id": 1,'


def test_export_json_writes_utf8(tmp_path):
    target = tmp_path / "tasks.json"
    export_json([Task(title="Café visit", tags=["naïve"])], str(target))
    raw = target.read_bytes()
    assert "Café visit".encode("utf-8") in raw
    assert json.loads(raw.decode("utf-8"))[0]["tags"] == ["naïve"]


def test_export_json_empty_list(tmp_path):
    target = tmp_path / "empty.json"
    assert export_json([], str(target)) == 0
    assert json.loads(target.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("path", ["", "   "])
def test_export_json_rejects_blank_path(path):
    with pytest.raises(ValueError):
        export_json([Task(title="Buy milk")], path)


def test_export_json_missing_parent_directory_raises(tmp_path, caplog):
    with caplog.at_level(logging.ERROR, logger="taskboard.export"):
        with pytest.raises(FileNotFoundError):
            export_json([Task(title="Buy milk")], str(tmp_path / "missing" / "tasks.json"))
    assert "could not write JSON export" in caplog.text


def test_export_json_logs_count(tasks, tmp_path, caplog):
    with caplog.at_level(logging.INFO, logger="taskboard.export"):
        export_json(tasks, str(tmp_path / "tasks.json"))
    assert "exported 3 tasks" in caplog.text
