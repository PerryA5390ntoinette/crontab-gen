"""Tests for crontab_gen.heatmap."""
from __future__ import annotations

import pytest

from crontab_gen.heatmap import HeatmapResult, build_heatmap


class TestHeatmapResult:
    def test_total_fires_sums_correctly(self):
        r = HeatmapResult(expression="* * * * *", fires_per_hour=[i for i in range(24)])
        assert r.total_fires == sum(range(24))

    def test_peak_hour_returns_index_of_max(self):
        fires = [0] * 24
        fires[14] = 10
        r = HeatmapResult(expression="0 14 * * *", fires_per_hour=fires)
        assert r.peak_hour == 14

    def test_str_contains_expression(self):
        r = HeatmapResult(expression="0 9 * * *", fires_per_hour=[0] * 24)
        assert "0 9 * * *" in str(r)

    def test_str_contains_all_hours(self):
        r = HeatmapResult(expression="* * * * *", fires_per_hour=[1] * 24)
        output = str(r)
        for h in range(24):
            assert f"{h:02d}:00" in output

    def test_str_contains_peak_hour(self):
        fires = [0] * 24
        fires[3] = 5
        r = HeatmapResult(expression="0 3 * * *", fires_per_hour=fires)
        assert "03:00" in str(r)
        assert "Peak hour" in str(r)

    def test_str_contains_total_fires(self):
        fires = [2] * 24
        r = HeatmapResult(expression="*/30 * * * *", fires_per_hour=fires)
        assert "Total fires" in str(r)
        assert str(sum(fires)) in str(r)


class TestBuildHeatmap:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            build_heatmap("not valid")

    def test_returns_heatmap_result(self):
        result = build_heatmap("0 * * * *", days=1)
        assert isinstance(result, HeatmapResult)

    def test_fires_per_hour_has_24_entries(self):
        result = build_heatmap("0 * * * *", days=1)
        assert len(result.fires_per_hour) == 24

    def test_every_minute_has_nonzero_fires(self):
        result = build_heatmap("* * * * *", days=1)
        assert all(v > 0 for v in result.fires_per_hour)

    def test_hourly_fires_only_in_minute_zero(self):
        # "0 * * * *" fires once per hour; each hour bucket should be >= 1
        result = build_heatmap("0 * * * *", days=2)
        assert all(v >= 1 for v in result.fires_per_hour)

    def test_expression_preserved(self):
        expr = "30 6 * * 1"
        result = build_heatmap(expr, days=7)
        assert result.expression == expr

    def test_specific_hour_expression_concentrates_fires(self):
        result = build_heatmap("* 3 * * *", days=3)
        # All fires should be in hour 3
        for h, count in enumerate(result.fires_per_hour):
            if h == 3:
                assert count > 0
            else:
                assert count == 0
