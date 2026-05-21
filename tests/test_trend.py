"""Tests for crontab_gen.trend."""
from __future__ import annotations

import json
import pathlib
import pytest

from crontab_gen.trend import TrendEntry, TrendReport, build_trend, top_expressions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_history(path: pathlib.Path, records: list[dict]) -> None:
    path.write_text(json.dumps(records))


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.json"


# ---------------------------------------------------------------------------
# TrendEntry
# ---------------------------------------------------------------------------

class TestTrendEntry:
    def test_str_contains_expression(self):
        e = TrendEntry(expression="* * * * *", count=3, last_used="2024-01-01T00:00:00")
        assert "* * * * *" in str(e)

    def test_str_contains_count(self):
        e = TrendEntry(expression="0 * * * *", count=7, last_used="2024-01-01T00:00:00")
        assert "7" in str(e)

    def test_str_contains_last_used(self):
        ts = "2024-06-15T12:00:00"
        e = TrendEntry(expression="0 0 * * *", count=1, last_used=ts)
        assert ts in str(e)


# ---------------------------------------------------------------------------
# TrendReport
# ---------------------------------------------------------------------------

class TestTrendReport:
    def test_empty_report_str(self):
        report = TrendReport()
        assert "No history" in str(report)

    def test_top_returns_limited_results(self):
        entries = [
            TrendEntry(expression=f"{i} * * * *", count=i, last_used="2024-01-01T00:00:00")
            for i in range(10)
        ]
        report = TrendReport(entries=entries)
        assert len(report.top(3)) == 3

    def test_top_sorted_by_count_descending(self):
        entries = [
            TrendEntry(expression="a", count=1, last_used="2024-01-01T00:00:00"),
            TrendEntry(expression="b", count=5, last_used="2024-01-01T00:00:00"),
            TrendEntry(expression="c", count=3, last_used="2024-01-01T00:00:00"),
        ]
        report = TrendReport(entries=entries)
        top = report.top(3)
        assert top[0].expression == "b"
        assert top[1].expression == "c"

    def test_str_contains_header(self):
        entries = [TrendEntry(expression="* * * * *", count=2, last_used="2024-01-01T00:00:00")]
        report = TrendReport(entries=entries)
        assert "trends" in str(report).lower()


# ---------------------------------------------------------------------------
# build_trend
# ---------------------------------------------------------------------------

class TestBuildTrend:
    def test_empty_history_returns_empty_report(self, hist_file):
        _write_history(hist_file, [])
        report = build_trend(str(hist_file))
        assert report.entries == []

    def test_counts_repeated_expressions(self, hist_file):
        records = [
            {"expression": "* * * * *", "created_at": "2024-01-01T00:00:00"},
            {"expression": "* * * * *", "created_at": "2024-01-02T00:00:00"},
            {"expression": "0 * * * *", "created_at": "2024-01-01T00:00:00"},
        ]
        _write_history(hist_file, records)
        report = build_trend(str(hist_file))
        counts = {e.expression: e.count for e in report.entries}
        assert counts["* * * * *"] == 2
        assert counts["0 * * * *"] == 1

    def test_last_used_is_most_recent(self, hist_file):
        records = [
            {"expression": "* * * * *", "created_at": "2024-01-01T00:00:00"},
            {"expression": "* * * * *", "created_at": "2024-06-01T00:00:00"},
        ]
        _write_history(hist_file, records)
        report = build_trend(str(hist_file))
        entry = next(e for e in report.entries if e.expression == "* * * * *")
        assert entry.last_used == "2024-06-01T00:00:00"


# ---------------------------------------------------------------------------
# top_expressions
# ---------------------------------------------------------------------------

class TestTopExpressions:
    def test_returns_tuples(self, hist_file):
        records = [{"expression": "* * * * *", "created_at": "2024-01-01T00:00:00"}]
        _write_history(hist_file, records)
        result = top_expressions(n=5, history_path=str(hist_file))
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)

    def test_respects_n_limit(self, hist_file):
        records = [
            {"expression": f"{i} * * * *", "created_at": "2024-01-01T00:00:00"}
            for i in range(8)
        ]
        _write_history(hist_file, records)
        result = top_expressions(n=3, history_path=str(hist_file))
        assert len(result) == 3
