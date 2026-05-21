"""Tests for crontab_gen.throttle."""
import pytest

from crontab_gen.throttle import (
    ThrottleWarning,
    ThrottleResult,
    analyse,
)


class TestThrottleWarning:
    def test_str_contains_expression(self):
        w = ThrottleWarning(expression="* * * * *", min_gap_seconds=60, threshold_seconds=120)
        assert "* * * * *" in str(w)

    def test_str_contains_gap(self):
        w = ThrottleWarning(expression="* * * * *", min_gap_seconds=60, threshold_seconds=120)
        assert "60" in str(w)

    def test_str_contains_threshold(self):
        w = ThrottleWarning(expression="* * * * *", min_gap_seconds=60, threshold_seconds=120)
        assert "120" in str(w)


class TestThrottleResult:
    def test_ok_when_no_warnings(self):
        result = ThrottleResult(expression="0 * * * *", warnings=[])
        assert result.ok is True

    def test_not_ok_when_warnings_present(self):
        w = ThrottleWarning(expression="* * * * *", min_gap_seconds=60, threshold_seconds=120)
        result = ThrottleResult(expression="* * * * *", warnings=[w])
        assert result.ok is False

    def test_str_ok(self):
        result = ThrottleResult(expression="0 * * * *", warnings=[])
        assert "OK" in str(result)

    def test_str_with_warnings_contains_header(self):
        w = ThrottleWarning(expression="* * * * *", min_gap_seconds=60, threshold_seconds=120)
        result = ThrottleResult(expression="* * * * *", warnings=[w])
        assert "THROTTLE WARNINGS" in str(result)


class TestAnalyse:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse("not a cron")

    def test_every_minute_below_default_threshold(self):
        result = analyse("* * * * *", threshold_seconds=120)
        assert not result.ok
        assert len(result.warnings) == 1

    def test_hourly_above_default_threshold(self):
        result = analyse("0 * * * *", threshold_seconds=60)
        assert result.ok
        assert len(result.warnings) == 0

    def test_returns_throttle_result(self):
        result = analyse("0 0 * * *")
        assert isinstance(result, ThrottleResult)

    def test_expression_preserved_in_result(self):
        expr = "0 12 * * *"
        result = analyse(expr)
        assert result.expression == expr

    def test_custom_threshold_triggers_warning_for_hourly(self):
        # threshold of 2 hours (7200s) should flag hourly jobs
        result = analyse("0 * * * *", threshold_seconds=7200)
        assert not result.ok

    def test_warning_expression_matches(self):
        expr = "* * * * *"
        result = analyse(expr, threshold_seconds=120)
        assert result.warnings[0].expression == expr
