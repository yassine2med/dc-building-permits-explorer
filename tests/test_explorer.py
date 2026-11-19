from datetime import date

import pytest

from permitexplorer.__main__ import main
from permitexplorer.core import PermitRecord, bar_chart, cost_by, count_by, filter_records, load

ROWS = [
    PermitRecord("1", "Electrical", "Ward 1", "Issued", date(2025, 1, 5), 100.0),
    PermitRecord("2", "Electrical", "Ward 2", "Final", date(2025, 1, 20), 300.0),
    PermitRecord("3", "Plumbing", "Ward 1", "Issued", date(2025, 3, 2), 50.0),
    PermitRecord("4", "Plumbing", "Ward 1", "Issued", date(2026, 3, 9), 50.0),
]


def test_count_by_kind_sorted_by_count_then_name():
    assert count_by(ROWS, "kind") == [("Electrical", 2), ("Plumbing", 2)]


def test_count_by_ward():
    assert count_by(ROWS, "ward")[0] == ("Ward 1", 3)


def test_count_by_month_is_chronological():
    assert [k for k, _ in count_by(ROWS, "month")] == ["2025-01", "2025-03", "2026-03"]


def test_count_by_bad_field():
    with pytest.raises(ValueError):
        count_by(ROWS, "color")


def test_cost_by_kind():
    assert cost_by(ROWS, "kind") == [("Electrical", 400.0), ("Plumbing", 100.0)]


def test_cost_by_bad_field():
    with pytest.raises(ValueError):
        cost_by(ROWS, "status")


def test_filter_by_kind_is_case_insensitive():
    assert len(filter_records(ROWS, kind="plumbing")) == 2


def test_filter_by_year_and_ward():
    assert [r.permit_id for r in filter_records(ROWS, ward="Ward 1", year=2025)] == ["1", "3"]


def test_bar_chart_scales_to_width():
    text = bar_chart([("a", 10), ("b", 5)], width=10)
    lines = text.splitlines()
    assert lines[0].count("#") == 10 and lines[1].count("#") == 5


def test_bar_chart_empty():
    assert bar_chart([]) == "(no data)"


def test_load_sample_data():
    assert len(load("data/permits.csv")) == 80


def test_load_bad_date(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("permit_id,type,ward,status,issued,cost\n1,Electrical,Ward 1,Issued,not-a-date,10\n")
    with pytest.raises(ValueError, match="line 2"):
        load(f)


def test_load_missing_columns(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("permit_id\n1\n")
    with pytest.raises(ValueError, match="missing columns"):
        load(f)


def test_cli_summary(capsys):
    assert main(["summary", "data/permits.csv"]) == 0
    assert "Permits: 80" in capsys.readouterr().out


def test_cli_bad_file():
    assert main(["count", "missing.csv"]) == 2
