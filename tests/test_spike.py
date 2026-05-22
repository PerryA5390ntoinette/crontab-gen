"""Tests for crontab_gen.spike."""
from __future__ import annotations

import pytest

from crontab_gen.spike import (
    SpikeWarning,
    SpikeResult,
    detect_spike,
)


# ---------------------------------------------------------------------------
# SpikeWarning
# ---------------------------------------------------------------------------

class TestSpikeWarning:
    def test_str_contains_expression(self):
        w = SpikeWarning(expression="* * * * *", window_minutes=60, count=61, threshold=10)
        assert "* * * * *" in str(w)

    def test_str_contains_count(self):
        w = SpikeWarning(expression="* * * * *", window_minutes=60, count=61, threshold=10)
        assert "61" in str(w)

    def test_str_contains_threshold(self):
        w = SpikeWarning(expression="* * * * *", window_minutes=60, count=61, threshold=10)
        assert "10" in str(w)

    def test_str_contains_window(self):
        w = SpikeWarning(expression="* * * * *", window_minutes=60, count=61, threshold=10)
        assert "60" in str(w)


# ---------------------------------------------------------------------------
# SpikeResult
# ---------------------------------------------------------------------------

class TestSpikeResult:
    def _ok_result(self):
        return SpikeResult(
            expression="0 * * * *",
            window_minutes=60,
            threshold=10,
            fires=1,
            warnings=[],
        )

    def _bad_result(self):
        w = SpikeWarning(expression="* * * * *", window_minutes=60, count=61, threshold=10)
        return SpikeResult(
            expression="* * * * *",
            window_minutes=60,
            threshold=10,
            fires=61,
            warnings=[w],
        )

    def test_ok_when_no_warnings(self):
        assert self._ok_result().ok() is True

    def test_not_ok_when_warnings(self):
        assert self._bad_result().ok() is False

    def test_str_ok_contains_expression(self):
        assert "0 * * * *" in str(self._ok_result())

    def test_str_ok_contains_fires(self):
        assert "1" in str(self._ok_result())

    def test_str_spike_contains_expression(self):
        assert "* * * * *" in str(self._bad_result())

    def test_str_spike_contains_detected(self):
        assert "SPIKE" in str(self._bad_result()).upper()


# ---------------------------------------------------------------------------
# detect_spike
# ---------------------------------------------------------------------------

class TestDetectSpike:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            detect_spike("not a cron")

    def test_every_minute_exceeds_default_threshold(self):
        result = detect_spike("* * * * *", window_minutes=60, threshold=10)
        assert not result.ok()
        assert result.fires > 10

    def test_hourly_within_default_threshold(self):
        result = detect_spike("0 * * * *", window_minutes=60, threshold=10)
        assert result.ok()
        assert result.fires <= 10

    def test_returns_spike_result_type(self):
        result = detect_spike("0 * * * *")
        assert isinstance(result, SpikeResult)

    def test_custom_threshold_triggers_warning(self):
        # hourly fires once per hour; threshold=0 should trigger
        result = detect_spike("0 * * * *", window_minutes=60, threshold=0)
        assert not result.ok()

    def test_fires_attribute_is_non_negative(self):
        result = detect_spike("0 0 * * *", window_minutes=60, threshold=5)
        assert result.fires >= 0

    def test_warning_attributes_match_result(self):
        result = detect_spike("* * * * *", window_minutes=60, threshold=10)
        assert not result.ok()
        w = result.warnings[0]
        assert w.expression == "* * * * *"
        assert w.threshold == 10
        assert w.window_minutes == 60
