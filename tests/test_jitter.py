"""Tests for crontab_gen.jitter."""
import pytest

from crontab_gen.jitter import (
    JitterSuggestion,
    JitterResult,
    analyse_jitter,
    _is_predictable,
    _fires_per_hour,
)


class TestJitterSuggestion:
    def test_str_contains_variant(self):
        s = JitterSuggestion("* * * * *", "7 * * * *", "shifted")
        assert "7 * * * *" in str(s)

    def test_str_contains_original(self):
        s = JitterSuggestion("* * * * *", "7 * * * *", "shifted")
        assert "* * * * *" in str(s)

    def test_str_contains_description(self):
        s = JitterSuggestion("* * * * *", "7 * * * *", "shifted to minute 7")
        assert "shifted to minute 7" in str(s)


class TestJitterResult:
    def test_str_contains_expression(self):
        r = JitterResult(expression="0 * * * *", fires_per_hour=1, predictable=True)
        assert "0 * * * *" in str(r)

    def test_str_contains_fires_per_hour(self):
        r = JitterResult(expression="0 * * * *", fires_per_hour=1, predictable=True)
        assert "1" in str(r)

    def test_str_contains_status_predictable(self):
        r = JitterResult(expression="0 * * * *", fires_per_hour=1, predictable=True)
        assert "predictable" in str(r)

    def test_str_contains_status_varied(self):
        r = JitterResult(expression="7 * * * *", fires_per_hour=1, predictable=False)
        assert "varied" in str(r)

    def test_str_lists_suggestions(self):
        s = JitterSuggestion("* * * * *", "7 * * * *", "shifted")
        r = JitterResult(
            expression="* * * * *",
            fires_per_hour=60,
            predictable=True,
            suggestions=[s],
        )
        assert "7 * * * *" in str(r)


class TestIsPredictable:
    def test_wildcard_minute_is_predictable(self):
        assert _is_predictable("* * * * *") is True

    def test_fixed_minute_is_predictable(self):
        assert _is_predictable("0 * * * *") is True

    def test_range_minute_is_not_predictable(self):
        assert _is_predictable("0-5 * * * *") is False

    def test_step_minute_is_not_predictable(self):
        assert _is_predictable("*/15 * * * *") is False

    def test_invalid_parts_returns_false(self):
        assert _is_predictable("bad expression") is False


class TestAnalyseJitter:
    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_jitter("not valid")

    def test_returns_jitter_result(self):
        result = analyse_jitter("0 * * * *")
        assert isinstance(result, JitterResult)

    def test_predictable_expression_has_suggestions(self):
        result = analyse_jitter("0 * * * *")
        assert result.predictable is True
        assert len(result.suggestions) > 0

    def test_step_expression_not_predictable(self):
        result = analyse_jitter("*/15 * * * *")
        assert result.predictable is False
        assert result.suggestions == []

    def test_fires_per_hour_every_minute(self):
        result = analyse_jitter("* * * * *")
        assert result.fires_per_hour == 60

    def test_fires_per_hour_once_per_hour(self):
        result = analyse_jitter("0 * * * *")
        assert result.fires_per_hour == 1

    def test_suggestion_variants_are_valid_expressions(self):
        from crontab_gen.expression import is_valid
        result = analyse_jitter("0 * * * *")
        for s in result.suggestions:
            assert is_valid(s.variant), f"{s.variant!r} should be valid"
