"""Tests for crontab_gen.next_run."""

from datetime import datetime

import pytest

from crontab_gen.next_run import next_runs


_ANCHOR = datetime(2024, 1, 15, 12, 0)  # Monday 2024-01-15 12:00


class TestNextRunsValidation:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            next_runs("not a cron", after=_ANCHOR)

    def test_returns_list(self):
        result = next_runs("* * * * *", count=3, after=_ANCHOR)
        assert isinstance(result, list)

    def test_returns_correct_count(self):
        result = next_runs("* * * * *", count=5, after=_ANCHOR)
        assert len(result) == 5

    def test_returns_datetime_objects(self):
        result = next_runs("* * * * *", count=1, after=_ANCHOR)
        assert isinstance(result[0], datetime)


class TestNextRunsEveryMinute:
    def test_consecutive_minutes(self):
        result = next_runs("* * * * *", count=3, after=_ANCHOR)
        assert result[0] == datetime(2024, 1, 15, 12, 1)
        assert result[1] == datetime(2024, 1, 15, 12, 2)
        assert result[2] == datetime(2024, 1, 15, 12, 3)


class TestNextRunsSpecificTime:
    def test_daily_at_fixed_time(self):
        # Every day at 09:30
        result = next_runs("30 9 * * *", count=2, after=_ANCHOR)
        assert result[0] == datetime(2024, 1, 16, 9, 30)
        assert result[1] == datetime(2024, 1, 17, 9, 30)

    def test_hourly_on_the_hour(self):
        result = next_runs("0 * * * *", count=3, after=_ANCHOR)
        assert result[0] == datetime(2024, 1, 15, 13, 0)
        assert result[1] == datetime(2024, 1, 15, 14, 0)
        assert result[2] == datetime(2024, 1, 15, 15, 0)


class TestNextRunsStep:
    def test_every_15_minutes(self):
        anchor = datetime(2024, 1, 15, 12, 0)
        result = next_runs("*/15 * * * *", count=4, after=anchor)
        assert result[0] == datetime(2024, 1, 15, 12, 15)
        assert result[1] == datetime(2024, 1, 15, 12, 30)
        assert result[2] == datetime(2024, 1, 15, 12, 45)
        assert result[3] == datetime(2024, 1, 15, 13, 0)


class TestNextRunsAfterDefault:
    def test_after_defaults_to_now(self):
        """Smoke-test: without *after*, results should be in the future."""
        before = datetime.now()
        result = next_runs("* * * * *", count=1)
        assert result[0] > before
