import csv

from taskboard.export import HEADER, export_csv
from taskboard.models import Task


def test_export_writes_header_and_rows(tmp_path):
    path = tmp_path / "tasks.csv"
    tasks = [Task(title="Buy milk", id=1, tags=["home", "errand"]), Task(title="Walk dog", id=2)]
    assert export_csv(tasks, str(path)) == 2
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == HEADER
    assert rows[1][1] == "Buy milk"
    assert rows[1][5] == "home;errand"
