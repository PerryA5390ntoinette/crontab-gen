"""Tests for crontab_gen.idle."""
from __future__ import annotations

import pytest

from crontab_gen.idle import IdleGap, IdleResult, analyse_idle


# ---------------------------------------------------------------------------
# IdleGap
# ---------------------------------------------------------------------------

class TestIdleGap:
    def test_str_contains_gap_minutes(self):
        g = IdleGap(start="2024-01-01 00:00", end="2024-01-01 02:00", gap_minutes=120)
        assert "120" in str(g)

    def test_str_contains_start_and_end(self):
        g = IdleGap(start="2024-01-01 00:00", end="2024-01-01 01:00", gap_minutes=60)
        assert "2024-01-01 00:00" in str(g)
        assert "2024-01-01 01:00" in str(g)


# ---------------------------------------------------------------------------
# IdleResult
# ---------------------------------------------------------------------------

class TestIdleResult:
    def _make(self, gaps, threshold=60):
        return IdleResult(
            expression="0 * * * *",
            gaps=gaps,
            threshold_minutes=threshold,
        )

    def test_max_gap_empty(self):
        result = self._make([])
        assert result.max_gap == 0

    def test_max_gap_returns_largest(self):
        gaps = [
            IdleGap("a", "b", 30),
            IdleGap("b", "c", 90),
            IdleGap("c", "d", 45),
        ]
        assert self._make(gaps).max_gap == 90

    def test_long_gaps_filtered_by_threshold(self):
        gaps = [
            IdleGap("a", "b", 30),
            IdleGap("b", "c", 120),
        ]
        result = self._make(gaps, threshold=60)
        assert len(result.long_gaps) == 1
        assert result.long_gaps[0].gap_minutes == 120

    def test_has_long_gaps_false_when_all_short(self):
        gaps = [IdleGap("a", "b", 10)]
        assert not self._make(gaps, threshold=60).has_long_gaps

    def test_has_long_gaps_true_when_exceeds_threshold(self):
        gaps = [IdleGap("a", "b", 120)]
        assert self._make(gaps, threshold=60).has_long_gaps

    def test_str_contains_expression(self):
        result = self._make([])
        assert "0 * * * *" in str(result)

    def test_str_contains_threshold(self):
        result = self._make([], threshold=90)
        assert "90" in str(result)

    def test_str_contains_max_gap_when_gaps_present(self):
        gaps = [IdleGap("a", "b", 75)]
        result = self._make(gaps)
        assert "75" in str(result)


# ---------------------------------------------------------------------------
# analyse_idle
# ---------------------------------------------------------------------------

class TestAnalyseIdle:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron"):
            analyse_idle("not valid")

    def test_returns_idle_result(self):
        result = analyse_idle("* * * * *", horizon_hours=1)
        assert isinstance(result, IdleResult)

    def test_every_minute_has_one_minute_gaps(self):
        result = analyse_idle("* * * * *", horizon_hours=1)
        assert result.gaps, "Expected at least one gap"
        for g in result.gaps:
            assert g.gap_minutes == 1

    def test_hourly_has_sixty_minute_gaps(self):
        result = analyse_idle("0 * * * *", horizon_hours=4, threshold_minutes=30)
        assert result.gaps
        for g in result.gaps:
            assert g.gap_minutes == 60

    def test_hourly_has_long_gaps_at_threshold_60(self):
        result = analyse_idle("0 * * * *", horizon_hours=4, threshold_minutes=60)
        assert result.has_long_gaps

    def test_expression_stored_on_result(self):
        expr = "0 12 * * *"
        result = analyse_idle(expr, horizon_hours=48)
        assert result.expression == expr
