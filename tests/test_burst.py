"""Tests for crontab_gen.burst."""
from __future__ import annotations

import pytest

from crontab_gen.burst import BurstWarning, BurstResult, detect_burst


# ---------------------------------------------------------------------------
# BurstWarning.__str__
# ---------------------------------------------------------------------------
class TestBurstWarning:
    def test_str_contains_expression(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        assert "* * * * *" in str(w)

    def test_str_contains_count(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        assert "60" in str(w)

    def test_str_contains_window(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        assert "60" in str(w)

    def test_str_contains_threshold(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        assert "10" in str(w)


# ---------------------------------------------------------------------------
# BurstResult.ok / __str__
# ---------------------------------------------------------------------------
class TestBurstResult:
    def test_ok_when_no_warnings(self):
        r = BurstResult(
            expression="0 * * * *",
            count=1,
            window_minutes=60,
            threshold=10,
            warnings=[],
        )
        assert r.ok is True

    def test_not_ok_when_warnings_present(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        r = BurstResult(
            expression="* * * * *",
            count=60,
            window_minutes=60,
            threshold=10,
            warnings=[w],
        )
        assert r.ok is False

    def test_str_ok_contains_ok(self):
        r = BurstResult(
            expression="0 * * * *",
            count=1,
            window_minutes=60,
            threshold=10,
            warnings=[],
        )
        assert "OK" in str(r)

    def test_str_not_ok_contains_burst(self):
        w = BurstWarning(expression="* * * * *", count=60, window_minutes=60, threshold=10)
        r = BurstResult(
            expression="* * * * *",
            count=60,
            window_minutes=60,
            threshold=10,
            warnings=[w],
        )
        assert "BURST" in str(r)


# ---------------------------------------------------------------------------
# detect_burst
# ---------------------------------------------------------------------------
class TestDetectBurst:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            detect_burst("not a cron")

    def test_every_minute_exceeds_default_threshold(self):
        result = detect_burst("* * * * *", window_minutes=60, threshold=10)
        assert result.ok is False

    def test_hourly_within_default_threshold(self):
        result = detect_burst("0 * * * *", window_minutes=60, threshold=10)
        assert result.ok is True

    def test_count_is_positive_integer(self):
        result = detect_burst("* * * * *", window_minutes=60, threshold=100)
        assert isinstance(result.count, int)
        assert result.count > 0

    def test_custom_threshold_respected(self):
        # every minute fires 60 times per hour; threshold=100 should be ok
        result = detect_burst("* * * * *", window_minutes=60, threshold=100)
        assert result.ok is True

    def test_result_expression_matches_input(self):
        expr = "*/5 * * * *"
        result = detect_burst(expr, window_minutes=60, threshold=20)
        assert result.expression == expr
