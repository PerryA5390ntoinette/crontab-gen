"""Integration tests: suggest results are valid cron expressions."""

from __future__ import annotations

import pytest

from crontab_gen.suggest import suggest, _SUGGESTIONS
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain


class TestSuggestIntegration:
    def test_all_builtin_expressions_are_valid(self):
        for s in _SUGGESTIONS:
            assert is_valid(s.expression), f"Invalid expression: {s.expression}"

    def test_suggest_results_are_valid_expressions(self):
        queries = ["daily", "hourly", "monthly", "every 5 minutes", "business hours"]
        for q in queries:
            for suggestion in suggest(q):
                assert is_valid(suggestion.expression), (
                    f"Query '{q}' returned invalid expression: {suggestion.expression}"
                )

    def test_suggest_results_are_explainable(self):
        for suggestion in suggest("", limit=10):
            description = explain(suggestion.expression)
            assert isinstance(description, str)
            assert len(description) > 0

    def test_every_minute_suggestion_explainable(self):
        results = suggest("every minute")
        assert len(results) > 0
        desc = explain(results[0].expression)
        assert desc  # non-empty string

    def test_unique_expressions_in_results(self):
        results = suggest("", limit=20)
        expressions = [r.expression for r in results]
        assert len(expressions) == len(set(expressions)), "Duplicate expressions in results"
