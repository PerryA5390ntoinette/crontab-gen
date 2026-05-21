"""Tests for crontab_gen.quota."""
from __future__ import annotations

import pytest
from datetime import datetime

from crontab_gen.quota import QuotaWarning, QuotaResult, check_quota


REF = datetime(2024, 1, 1, 0, 0)


class TestQuotaWarning:
    def test_str_contains_expression(self):
        w = QuotaWarning(expression="* * * * *", window_hours=1, limit=10, actual=60)
        assert "* * * * *" in str(w)

    def test_str_contains_actual(self):
        w = QuotaWarning(expression="* * * * *", window_hours=1, limit=10, actual=60)
        assert "60" in str(w)

    def test_str_contains_limit(self):
        w = QuotaWarning(expression="* * * * *", window_hours=1, limit=10, actual=60)
        assert "10" in str(w)

    def test_str_contains_window(self):
        w = QuotaWarning(expression="* * * * *", window_hours=3, limit=10, actual=60)
        assert "3" in str(w)


class TestQuotaResult:
    def test_ok_when_no_warnings(self):
        r = QuotaResult(expression="0 * * * *", window_hours=24, limit=60, actual=24)
        assert r.ok is True

    def test_not_ok_when_warnings_present(self):
        w = QuotaWarning(expression="* * * * *", window_hours=1, limit=10, actual=60)
        r = QuotaResult(
            expression="* * * * *", window_hours=1, limit=10, actual=60, warnings=[w]
        )
        assert r.ok is False

    def test_str_ok_contains_ok(self):
        r = QuotaResult(expression="0 * * * *", window_hours=24, limit=60, actual=24)
        assert "OK" in str(r)

    def test_str_not_ok_contains_quota(self):
        w = QuotaWarning(expression="* * * * *", window_hours=1, limit=10, actual=60)
        r = QuotaResult(
            expression="* * * * *", window_hours=1, limit=10, actual=60, warnings=[w]
        )
        assert "QUOTA" in str(r)


class TestCheckQuota:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            check_quota("not valid", reference=REF)

    def test_every_minute_exceeds_default_limit_in_24h(self):
        result = check_quota("* * * * *", limit=60, window_hours=1, reference=REF)
        assert result.actual == 60
        assert result.ok is True  # exactly at limit

    def test_every_minute_exceeds_low_limit(self):
        result = check_quota("* * * * *", limit=30, window_hours=1, reference=REF)
        assert result.actual > 30
        assert result.ok is False

    def test_hourly_within_daily_limit(self):
        result = check_quota("0 * * * *", limit=24, window_hours=24, reference=REF)
        assert result.actual == 24
        assert result.ok is True

    def test_result_has_correct_expression(self):
        result = check_quota("0 0 * * *", reference=REF)
        assert result.expression == "0 0 * * *"

    def test_result_stores_limit_and_window(self):
        result = check_quota("0 0 * * *", limit=5, window_hours=48, reference=REF)
        assert result.limit == 5
        assert result.window_hours == 48
