"""Tests for crontab_gen.conflict."""
from __future__ import annotations

import pytest

from crontab_gen.conflict import ConflictPair, ConflictResult, detect_conflicts


class TestConflictPair:
    def test_has_shared_times(self):
        pair = ConflictPair("* * * * *", "*/2 * * * *", ["2024-01-01 00:00", "2024-01-01 00:02"])
        assert pair.shared_times == ["2024-01-01 00:00", "2024-01-01 00:02"]

    def test_attributes(self):
        pair = ConflictPair("0 * * * *", "0 9 * * *", ["2024-01-01 09:00"])
        assert pair.expr_a == "0 * * * *"
        assert pair.expr_b == "0 9 * * *"


class TestConflictResult:
    def test_no_conflicts(self):
        result = ConflictResult(expressions=["0 6 * * *", "0 7 * * *"], pairs=[])
        assert not result.has_conflicts

    def test_has_conflicts(self):
        pair = ConflictPair("* * * * *", "*/5 * * * *", ["2024-01-01 00:00"])
        result = ConflictResult(expressions=["* * * * *", "*/5 * * * *"], pairs=[pair])
        assert result.has_conflicts

    def test_expressions_stored(self):
        result = ConflictResult(expressions=["0 6 * * *", "0 7 * * *"])
        assert "0 6 * * *" in result.expressions


class TestDetectConflicts:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            detect_conflicts(["bad expr", "* * * * *"])

    def test_identical_expressions_conflict(self):
        result = detect_conflicts(["0 9 * * *", "0 9 * * *"], horizon=5)
        assert result.has_conflicts

    def test_non_overlapping_no_conflict(self):
        # 6 AM daily vs 7 AM daily — never overlap
        result = detect_conflicts(["0 6 * * *", "0 7 * * *"], horizon=30)
        assert not result.has_conflicts

    def test_returns_conflict_result(self):
        result = detect_conflicts(["* * * * *", "*/2 * * * *"], horizon=10)
        assert isinstance(result, ConflictResult)

    def test_pair_contains_both_expressions(self):
        result = detect_conflicts(["* * * * *", "*/2 * * * *"], horizon=10)
        assert result.has_conflicts
        pair = result.pairs[0]
        assert {pair.expr_a, pair.expr_b} == {"* * * * *", "*/2 * * * *"}

    def test_three_expressions_checks_all_pairs(self):
        # every minute conflicts with */2 and */3; */2 and */3 also overlap
        result = detect_conflicts(["* * * * *", "*/2 * * * *", "*/3 * * * *"], horizon=20)
        assert len(result.pairs) >= 2

    def test_shared_times_are_strings(self):
        result = detect_conflicts(["0 9 * * *", "0 9 * * *"], horizon=5)
        for t in result.pairs[0].shared_times:
            assert isinstance(t, str)

    def test_horizon_limits_sample(self):
        # With horizon=1 only one run is sampled; identical expressions still conflict
        result = detect_conflicts(["* * * * *", "* * * * *"], horizon=1)
        assert result.has_conflicts
