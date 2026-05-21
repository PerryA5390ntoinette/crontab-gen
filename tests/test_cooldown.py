"""Tests for crontab_gen.cooldown."""
import pytest

from crontab_gen.cooldown import (
    CooldownWarning,
    CooldownResult,
    check_cooldown,
)


class TestCooldownWarning:
    def test_str_contains_expressions(self):
        w = CooldownWarning(expr_a="* * * * *", expr_b="*/2 * * * *", gap_seconds=0, min_seconds=60)
        assert "* * * * *" in str(w)
        assert "*/2 * * * *" in str(w)

    def test_str_contains_gap(self):
        w = CooldownWarning(expr_a="* * * * *", expr_b="*/2 * * * *", gap_seconds=30, min_seconds=60)
        assert "30" in str(w)

    def test_str_contains_minimum(self):
        w = CooldownWarning(expr_a="* * * * *", expr_b="*/2 * * * *", gap_seconds=30, min_seconds=60)
        assert "60" in str(w)


class TestCooldownResult:
    def test_ok_when_no_warnings(self):
        result = CooldownResult(warnings=[])
        assert result.ok is True

    def test_not_ok_when_warnings_present(self):
        w = CooldownWarning("* * * * *", "*/2 * * * *", 0, 60)
        result = CooldownResult(warnings=[w])
        assert result.ok is False

    def test_str_ok(self):
        result = CooldownResult(warnings=[])
        assert "OK" in str(result)

    def test_str_with_warnings(self):
        w = CooldownWarning("* * * * *", "*/2 * * * *", 0, 60)
        result = CooldownResult(warnings=[w])
        text = str(result)
        assert "violation" in text.lower()


class TestCheckCooldown:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            check_cooldown(["not_valid", "* * * * *"])

    def test_identical_expressions_violate_cooldown(self):
        # Two identical every-minute expressions always fire at the same time
        result = check_cooldown(["* * * * *", "* * * * *"], min_seconds=60)
        assert not result.ok

    def test_well_separated_expressions_pass(self):
        # One fires at minute 0, the other at minute 30 — 30 min apart
        result = check_cooldown(["0 * * * *", "30 * * * *"], min_seconds=60)
        assert result.ok

    def test_returns_cooldown_result(self):
        result = check_cooldown(["* * * * *", "*/5 * * * *"], min_seconds=60)
        assert isinstance(result, CooldownResult)

    def test_single_expression_never_violates(self):
        result = check_cooldown(["* * * * *"], min_seconds=60)
        assert result.ok

    def test_empty_list_never_violates(self):
        result = check_cooldown([], min_seconds=60)
        assert result.ok

    def test_warning_fields_populated(self):
        result = check_cooldown(["* * * * *", "* * * * *"], min_seconds=60)
        assert len(result.warnings) >= 1
        w = result.warnings[0]
        assert w.min_seconds == 60
        assert isinstance(w.gap_seconds, int)
