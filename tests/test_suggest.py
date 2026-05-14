"""Tests for crontab_gen.suggest."""

from __future__ import annotations

import pytest

from crontab_gen.suggest import Suggestion, suggest, _SUGGESTIONS


class TestSuggestion:
    def test_str_contains_expression(self):
        s = Suggestion("0 * * * *", "Every hour", ["hourly"])
        assert "0 * * * *" in str(s)

    def test_str_contains_description(self):
        s = Suggestion("0 * * * *", "Every hour", ["hourly"])
        assert "Every hour" in str(s)


class TestSuggest:
    def test_empty_query_returns_defaults(self):
        results = suggest("")
        assert len(results) > 0

    def test_empty_query_respects_limit(self):
        results = suggest("", limit=3)
        assert len(results) == 3

    def test_hourly_keyword(self):
        results = suggest("hourly")
        assert any("0 * * * *" == r.expression for r in results)

    def test_daily_keyword(self):
        results = suggest("daily")
        expressions = [r.expression for r in results]
        assert "0 0 * * *" in expressions

    def test_every_5_minutes(self):
        results = suggest("every 5 minutes")
        assert any("*/5 * * * *" == r.expression for r in results)

    def test_monthly_keyword(self):
        results = suggest("monthly")
        assert any("0 0 1 * *" == r.expression for r in results)

    def test_no_match_returns_empty(self):
        results = suggest("zzznomatch")
        assert results == []

    def test_limit_is_respected(self):
        results = suggest("every", limit=2)
        assert len(results) <= 2

    def test_returns_suggestion_objects(self):
        results = suggest("daily")
        for r in results:
            assert isinstance(r, Suggestion)

    def test_business_hours_keyword(self):
        results = suggest("business hours")
        assert any("0 9-17 * * 1-5" == r.expression for r in results)

    def test_whitespace_only_query_returns_defaults(self):
        results = suggest("   ")
        assert len(results) > 0

    def test_all_suggestions_have_five_field_expressions(self):
        for s in _SUGGESTIONS:
            parts = s.expression.split()
            assert len(parts) == 5, f"Bad expression: {s.expression}"
