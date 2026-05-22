"""Tests for crontab_gen.forecast."""
from __future__ import annotations

import pytest
from datetime import datetime

from crontab_gen.forecast import ForecastResult, build_forecast


FIXED = datetime(2024, 1, 15, 12, 0, 0)


class TestForecastResult:
    def _make(self, fires=None):
        return ForecastResult(
            expression="* * * * *",
            horizon_hours=1,
            fires=fires or [],
        )

    def test_count_empty(self):
        assert self._make().count == 0

    def test_count_non_empty(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(3)]
        assert self._make(fires).count == 3

    def test_first_none_when_empty(self):
        assert self._make().first is None

    def test_last_none_when_empty(self):
        assert self._make().last is None

    def test_first_returns_earliest(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(3)]
        result = self._make(fires)
        assert result.first == fires[0]

    def test_last_returns_latest(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(3)]
        result = self._make(fires)
        assert result.last == fires[-1]

    def test_str_contains_expression(self):
        assert "* * * * *" in str(self._make())

    def test_str_contains_horizon(self):
        assert "1h" in str(self._make())

    def test_str_contains_fire_count(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(3)]
        assert "3" in str(self._make(fires))

    def test_str_shows_and_more_when_over_five(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(10)]
        assert "more" in str(self._make(fires))

    def test_str_no_more_when_five_or_fewer(self):
        fires = [datetime(2024, 1, 15, 12, i) for i in range(4)]
        assert "more" not in str(self._make(fires))


class TestBuildForecast:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid"):
            build_forecast("not valid", from_dt=FIXED)

    def test_zero_horizon_raises(self):
        with pytest.raises(ValueError, match="horizon_hours"):
            build_forecast("* * * * *", horizon_hours=0, from_dt=FIXED)

    def test_returns_forecast_result(self):
        result = build_forecast("* * * * *", horizon_hours=1, from_dt=FIXED)
        assert isinstance(result, ForecastResult)

    def test_every_minute_fills_hour(self):
        result = build_forecast("* * * * *", horizon_hours=1, from_dt=FIXED)
        assert result.count == 60

    def test_hourly_fires_once_in_one_hour(self):
        result = build_forecast("0 * * * *", horizon_hours=1, from_dt=FIXED)
        assert result.count == 1

    def test_daily_fires_once_in_24h(self):
        start = datetime(2024, 1, 15, 0, 0)
        result = build_forecast("0 0 * * *", horizon_hours=24, from_dt=start)
        assert result.count == 1

    def test_fires_are_within_horizon(self):
        from datetime import timedelta
        result = build_forecast("* * * * *", horizon_hours=2, from_dt=FIXED)
        deadline = FIXED + timedelta(hours=2)
        assert all(dt < deadline for dt in result.fires)

    def test_expression_preserved(self):
        result = build_forecast("0 9 * * 1", horizon_hours=24, from_dt=FIXED)
        assert result.expression == "0 9 * * 1"

    def test_horizon_preserved(self):
        result = build_forecast("* * * * *", horizon_hours=6, from_dt=FIXED)
        assert result.horizon_hours == 6
