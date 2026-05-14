"""Tests for crontab_gen.schedule."""

import pytest

from crontab_gen.schedule import ScheduleSummary, summarise


class TestScheduleSummary:
    def test_str_returns_summary(self):
        s = ScheduleSummary("* * * * *", "Every minute")
        assert str(s) == "Every minute"

    def test_expression_attribute(self):
        s = ScheduleSummary("0 * * * *", "Every hour at minute 0")
        assert s.expression == "0 * * * *"


class TestSummarise:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            summarise("not valid")

    def test_every_minute(self):
        result = summarise("* * * * *")
        assert result.summary == "Every minute"

    def test_every_5_minutes(self):
        result = summarise("*/5 * * * *")
        assert result.summary == "Every 5 minutes"

    def test_every_1_minute_singular(self):
        result = summarise("*/1 * * * *")
        assert result.summary == "Every 1 minute"

    def test_every_15_minutes(self):
        result = summarise("*/15 * * * *")
        assert result.summary == "Every 15 minutes"

    def test_every_hour_at_minute(self):
        result = summarise("30 * * * *")
        assert result.summary == "Every hour at minute 30"

    def test_daily_at_midnight(self):
        result = summarise("0 0 * * *")
        assert result.summary == "Daily at 00:00"

    def test_daily_at_specific_time(self):
        result = summarise("30 3 * * *")
        assert result.summary == "Daily at 03:30"

    def test_daily_padding(self):
        result = summarise("5 9 * * *")
        assert result.summary == "Daily at 09:05"

    def test_weekly_on_monday(self):
        result = summarise("0 9 * * 1")
        assert result.summary == "Weekly on Monday at 09:00"

    def test_weekly_on_friday(self):
        result = summarise("30 17 * * 5")
        assert result.summary == "Weekly on Friday at 17:30"

    def test_weekly_on_sunday(self):
        result = summarise("0 0 * * 0")
        assert result.summary == "Weekly on Sunday at 00:00"

    def test_custom_fallback(self):
        result = summarise("0 0 1 1 *")
        assert "Custom schedule" in result.summary
        assert "0 0 1 1 *" in result.summary

    def test_returns_schedule_summary_instance(self):
        result = summarise("* * * * *")
        assert isinstance(result, ScheduleSummary)
