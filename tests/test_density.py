"""Tests for crontab_gen.density."""

from __future__ import annotations

import pytest

from crontab_gen.density import (
    DensityResult,
    _classify,
    analyse_density,
    _LOW_THRESHOLD,
    _HIGH_THRESHOLD,
)


# ---------------------------------------------------------------------------
# DensityResult unit tests
# ---------------------------------------------------------------------------

class TestDensityResult:
    def _make(self, fire_count: int = 10, window_hours: int = 24, label: str = "low") -> DensityResult:
        return DensityResult(
            expression="* * * * *",
            window_hours=window_hours,
            fire_count=fire_count,
            label=label,
        )

    def test_str_contains_expression(self):
        r = self._make()
        assert "* * * * *" in str(r)

    def test_str_contains_fire_count(self):
        r = self._make(fire_count=42)
        assert "42" in str(r)

    def test_str_contains_label(self):
        r = self._make(label="medium")
        assert "medium" in str(r)

    def test_str_contains_window(self):
        r = self._make(window_hours=48)
        assert "48" in str(r)

    def test_fires_per_hour_correct(self):
        r = self._make(fire_count=48, window_hours=24)
        assert r.fires_per_hour() == pytest.approx(2.0)

    def test_fires_per_hour_zero_window(self):
        r = self._make(fire_count=10, window_hours=0)
        assert r.fires_per_hour() == 0.0


# ---------------------------------------------------------------------------
# _classify tests
# ---------------------------------------------------------------------------

class TestClassify:
    def test_low_when_below_threshold(self):
        assert _classify(_LOW_THRESHOLD, 24) == "low"

    def test_medium_between_thresholds(self):
        assert _classify(_LOW_THRESHOLD + 1, 24) == "medium"

    def test_high_above_threshold(self):
        assert _classify(_HIGH_THRESHOLD + 1, 24) == "high"

    def test_normalises_by_window(self):
        # 24 fires in 48 h == 12 fires/24 h => low
        assert _classify(24, 48) == "low"


# ---------------------------------------------------------------------------
# analyse_density integration tests
# ---------------------------------------------------------------------------

class TestAnalyseDensity:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_density("not valid", window_hours=24)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError, match="window_hours"):
            analyse_density("* * * * *", window_hours=0)

    def test_returns_density_result(self):
        result = analyse_density("0 * * * *", window_hours=24)
        assert isinstance(result, DensityResult)

    def test_every_minute_is_high(self):
        result = analyse_density("* * * * *", window_hours=24)
        assert result.label == "high"

    def test_daily_expression_is_low(self):
        result = analyse_density("0 9 * * *", window_hours=24)
        assert result.label == "low"

    def test_fire_count_positive(self):
        result = analyse_density("0 * * * *", window_hours=24)
        assert result.fire_count > 0

    def test_expression_preserved(self):
        result = analyse_density("30 6 * * 1", window_hours=24)
        assert result.expression == "30 6 * * 1"
