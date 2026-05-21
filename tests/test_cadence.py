"""Tests for crontab_gen.cadence."""
from __future__ import annotations

import pytest

from crontab_gen.cadence import CadenceResult, analyse_cadence


class TestCadenceResult:
    def test_str_contains_expression(self):
        r = CadenceResult(expression="* * * * *", avg_gap_minutes=1.0, label="every minute", fires_per_day=1440.0)
        assert "* * * * *" in str(r)

    def test_str_contains_label(self):
        r = CadenceResult(expression="0 * * * *", avg_gap_minutes=60.0, label="hourly", fires_per_day=24.0)
        assert "hourly" in str(r)

    def test_str_contains_fires_per_day(self):
        r = CadenceResult(expression="0 * * * *", avg_gap_minutes=60.0, label="hourly", fires_per_day=24.0)
        assert "24.0" in str(r)

    def test_str_contains_avg_gap(self):
        r = CadenceResult(expression="0 * * * *", avg_gap_minutes=60.0, label="hourly", fires_per_day=24.0)
        assert "60.0" in str(r)


class TestAnalyseCadence:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_cadence("not valid")

    def test_returns_cadence_result(self):
        result = analyse_cadence("* * * * *")
        assert isinstance(result, CadenceResult)

    def test_every_minute_label(self):
        result = analyse_cadence("* * * * *")
        assert result.label == "every minute"

    def test_every_minute_gap_is_one(self):
        result = analyse_cadence("* * * * *")
        assert result.avg_gap_minutes == pytest.approx(1.0, abs=0.1)

    def test_hourly_label(self):
        result = analyse_cadence("0 * * * *")
        assert result.label == "hourly"

    def test_hourly_gap_is_sixty(self):
        result = analyse_cadence("0 * * * *")
        assert result.avg_gap_minutes == pytest.approx(60.0, abs=1.0)

    def test_daily_label(self):
        result = analyse_cadence("0 0 * * *")
        assert result.label == "daily"

    def test_fires_per_day_every_minute(self):
        result = analyse_cadence("* * * * *")
        assert result.fires_per_day == pytest.approx(1440.0, abs=1.0)

    def test_fires_per_day_hourly(self):
        result = analyse_cadence("0 * * * *")
        assert result.fires_per_day == pytest.approx(24.0, abs=0.5)

    def test_expression_preserved(self):
        expr = "*/5 * * * *"
        result = analyse_cadence(expr)
        assert result.expression == expr

    def test_custom_sample_size(self):
        result = analyse_cadence("* * * * *", sample=5)
        assert isinstance(result, CadenceResult)
