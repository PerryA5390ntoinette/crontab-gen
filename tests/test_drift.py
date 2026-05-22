"""Tests for crontab_gen.drift."""
from datetime import datetime, timedelta

import pytest

from crontab_gen.drift import DriftEntry, DriftReport, analyse_drift


class TestDriftEntry:
    def _make(self, offset_seconds: float = 0.0) -> DriftEntry:
        scheduled = datetime(2024, 1, 15, 10, 0)
        actual = scheduled + timedelta(seconds=offset_seconds)
        return DriftEntry(expression="0 10 * * *", scheduled=scheduled, actual=actual)

    def test_delta_seconds_positive_when_late(self):
        entry = self._make(offset_seconds=90)
        assert entry.delta_seconds == pytest.approx(90.0)

    def test_delta_seconds_negative_when_early(self):
        entry = self._make(offset_seconds=-45)
        assert entry.delta_seconds == pytest.approx(-45.0)

    def test_abs_delta_seconds_always_positive(self):
        entry = self._make(offset_seconds=-120)
        assert entry.abs_delta_seconds == pytest.approx(120.0)

    def test_str_contains_expression(self):
        entry = self._make(offset_seconds=30)
        assert "0 10 * * *" in str(entry)

    def test_str_contains_late_when_positive(self):
        entry = self._make(offset_seconds=30)
        assert "late" in str(entry)

    def test_str_contains_early_when_negative(self):
        entry = self._make(offset_seconds=-30)
        assert "early" in str(entry)


class TestDriftReport:
    def _make_report(self, offsets, threshold=60.0) -> DriftReport:
        expr = "*/5 * * * *"
        base = datetime(2024, 1, 15, 12, 0)
        entries = [
            DriftEntry(
                expression=expr,
                scheduled=base + timedelta(minutes=5 * i),
                actual=base + timedelta(minutes=5 * i, seconds=off),
            )
            for i, off in enumerate(offsets)
        ]
        return DriftReport(expression=expr, entries=entries, threshold_seconds=threshold)

    def test_ok_when_all_within_threshold(self):
        report = self._make_report([10, -20, 5], threshold=60.0)
        assert report.ok is True

    def test_not_ok_when_any_exceeds_threshold(self):
        report = self._make_report([10, 120, 5], threshold=60.0)
        assert report.ok is False

    def test_max_drift_returns_largest(self):
        report = self._make_report([10, 90, 30])
        assert report.max_drift is not None
        assert report.max_drift.abs_delta_seconds == pytest.approx(90.0)

    def test_max_drift_none_when_empty(self):
        report = DriftReport(expression="* * * * *", entries=[])
        assert report.max_drift is None

    def test_avg_drift_seconds_computed(self):
        report = self._make_report([60, -60])
        assert report.avg_drift_seconds == pytest.approx(0.0)

    def test_avg_drift_zero_when_no_entries(self):
        report = DriftReport(expression="* * * * *", entries=[])
        assert report.avg_drift_seconds == pytest.approx(0.0)

    def test_str_contains_expression(self):
        report = self._make_report([0])
        assert report.expression in str(report)

    def test_str_contains_status_ok(self):
        report = self._make_report([5], threshold=60.0)
        assert "OK" in str(report)

    def test_str_contains_drift_detected(self):
        report = self._make_report([200], threshold=60.0)
        assert "DRIFT DETECTED" in str(report)


class TestAnalyseDrift:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_drift("not a cron", [])

    def test_empty_actual_times_returns_empty_report(self):
        report = analyse_drift("0 * * * *", [])
        assert report.entries == []

    def test_returns_drift_report(self):
        base = datetime(2024, 3, 1, 9, 0)
        actuals = [base + timedelta(seconds=30)]
        report = analyse_drift("0 9 * * *", actuals, reference=base - timedelta(minutes=5))
        assert isinstance(report, DriftReport)
        assert len(report.entries) == 1

    def test_threshold_propagated(self):
        report = analyse_drift("* * * * *", [], threshold_seconds=120.0)
        assert report.threshold_seconds == pytest.approx(120.0)
