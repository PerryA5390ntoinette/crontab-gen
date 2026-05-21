"""Tests for crontab_gen.window."""
import pytest

from crontab_gen.window import WindowWarning, WindowResult, analyse_window


class TestWindowWarning:
    def test_str_contains_expression(self):
        w = WindowWarning(expression="* * * * *", count=100, start_hour=9, end_hour=17, threshold=20)
        assert "* * * * *" in str(w)

    def test_str_contains_count(self):
        w = WindowWarning(expression="* * * * *", count=100, start_hour=9, end_hour=17, threshold=20)
        assert "100" in str(w)

    def test_str_contains_threshold(self):
        w = WindowWarning(expression="* * * * *", count=100, start_hour=9, end_hour=17, threshold=20)
        assert "20" in str(w)

    def test_str_contains_hours(self):
        w = WindowWarning(expression="0 * * * *", count=5, start_hour=8, end_hour=18, threshold=3)
        assert "08:00" in str(w)
        assert "18:00" in str(w)


class TestWindowResult:
    def test_ok_when_no_warnings(self):
        result = WindowResult(expression="0 9 * * *", start_hour=9, end_hour=17, count=1)
        assert result.ok is True

    def test_not_ok_when_warnings_present(self):
        w = WindowWarning(expression="* * * * *", count=500, start_hour=9, end_hour=17, threshold=20)
        result = WindowResult(
            expression="* * * * *", start_hour=9, end_hour=17, count=500, warnings=[w]
        )
        assert result.ok is False

    def test_str_ok_contains_ok(self):
        result = WindowResult(expression="0 12 * * *", start_hour=9, end_hour=17, count=1)
        assert "OK" in str(result)

    def test_str_warning_contains_warning_text(self):
        w = WindowWarning(expression="* * * * *", count=500, start_hour=9, end_hour=17, threshold=20)
        result = WindowResult(
            expression="* * * * *", start_hour=9, end_hour=17, count=500, warnings=[w]
        )
        assert "Warning" in str(result)


class TestAnalyseWindow:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_window("not a cron")

    def test_invalid_hour_range_raises(self):
        with pytest.raises(ValueError, match="start_hour"):
            analyse_window("* * * * *", start_hour=18, end_hour=9)

    def test_returns_window_result(self):
        result = analyse_window("0 12 * * *", start_hour=9, end_hour=17)
        assert isinstance(result, WindowResult)

    def test_every_minute_exceeds_default_threshold(self):
        result = analyse_window("* * * * *", start_hour=0, end_hour=24, threshold=20)
        assert not result.ok
        assert result.count > 20

    def test_once_daily_outside_window_has_zero_count(self):
        # Fires at 03:00 daily; window is 09-17
        result = analyse_window("0 3 * * *", start_hour=9, end_hour=17, horizon_days=1)
        assert result.count == 0
        assert result.ok is True

    def test_once_daily_inside_window_has_count_one(self):
        result = analyse_window("0 12 * * *", start_hour=9, end_hour=17, horizon_days=1)
        assert result.count == 1
        assert result.ok is True

    def test_expression_stored_in_result(self):
        expr = "30 10 * * *"
        result = analyse_window(expr, start_hour=9, end_hour=17)
        assert result.expression == expr

    def test_hours_stored_in_result(self):
        result = analyse_window("0 12 * * *", start_hour=8, end_hour=20)
        assert result.start_hour == 8
        assert result.end_hour == 20
