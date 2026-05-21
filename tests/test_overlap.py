"""Tests for crontab_gen.overlap."""
from __future__ import annotations

import pytest

from crontab_gen.overlap import detect_overlap, overlap_matrix, OverlapResult


class TestDetectOverlap:
    def test_identical_expressions_have_overlap(self):
        result = detect_overlap("* * * * *", "* * * * *", lookahead=10)
        assert result.has_overlap

    def test_non_overlapping_expressions(self):
        # One fires at minute 0, the other at minute 30 — no shared minute in small sample
        result = detect_overlap("0 * * * *", "30 * * * *", lookahead=5)
        assert not result.has_overlap

    def test_result_contains_expressions(self):
        result = detect_overlap("* * * * *", "* * * * *", lookahead=5)
        assert result.expr_a == "* * * * *"
        assert result.expr_b == "* * * * *"

    def test_shared_times_are_strings(self):
        result = detect_overlap("* * * * *", "* * * * *", lookahead=3)
        for t in result.shared_times:
            assert isinstance(t, str)

    def test_invalid_expr_a_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            detect_overlap("not valid", "* * * * *")

    def test_invalid_expr_b_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            detect_overlap("* * * * *", "bad expr")

    def test_str_no_overlap(self):
        result = OverlapResult(expr_a="0 * * * *", expr_b="30 * * * *", shared_times=[])
        assert "No overlap" in str(result)

    def test_str_with_overlap(self):
        result = OverlapResult(
            expr_a="* * * * *",
            expr_b="* * * * *",
            shared_times=["2024-01-01 00:01", "2024-01-01 00:02"],
        )
        text = str(result)
        assert "2" in text
        assert "* * * * *" in text

    def test_str_truncates_long_shared_list(self):
        times = [f"2024-01-01 00:{i:02d}" for i in range(10)]
        result = OverlapResult(expr_a="a", expr_b="b", shared_times=times)
        assert "+5 more" in str(result)


class TestOverlapMatrix:
    def test_empty_when_no_overlap(self):
        pairs = overlap_matrix(["0 0 * * *", "0 12 * * *"], lookahead=5)
        assert pairs == []

    def test_returns_list_of_tuples(self):
        pairs = overlap_matrix(["* * * * *", "* * * * *"], lookahead=5)
        assert isinstance(pairs, list)
        if pairs:
            a, b, count = pairs[0]
            assert isinstance(a, str)
            assert isinstance(b, str)
            assert isinstance(count, int)

    def test_identical_expressions_appear_in_matrix(self):
        pairs = overlap_matrix(["* * * * *", "* * * * *"], lookahead=10)
        assert len(pairs) == 1
        assert pairs[0][2] > 0

    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            overlap_matrix(["* * * * *", "invalid"], lookahead=5)
