"""Tests for crontab_gen.retry."""
import pytest

from crontab_gen.retry import RetryPolicy, suggest_retry_policies


class TestRetryPolicy:
    def test_str_contains_expression(self):
        rp = RetryPolicy(
            expression="*/5 * * * *",
            interval_minutes=5,
            description="Every 5 minutes",
            jitter_note="Low risk.",
        )
        assert "*/5 * * * *" in str(rp)

    def test_str_contains_interval(self):
        rp = RetryPolicy(
            expression="*/10 * * * *",
            interval_minutes=10,
            description="Every 10 minutes",
            jitter_note="Balanced.",
        )
        assert "10m" in str(rp)

    def test_str_contains_description(self):
        rp = RetryPolicy(
            expression="0 * * * *",
            interval_minutes=60,
            description="Every hour",
            jitter_note="Low frequency.",
        )
        assert "Every hour" in str(rp)


class TestSuggestRetryPolicies:
    def test_returns_list(self):
        result = suggest_retry_policies()
        assert isinstance(result, list)

    def test_all_results_are_retry_policy_instances(self):
        for item in suggest_retry_policies():
            assert isinstance(item, RetryPolicy)

    def test_default_includes_common_intervals(self):
        intervals = {r.interval_minutes for r in suggest_retry_policies()}
        assert 5 in intervals
        assert 60 in intervals

    def test_max_interval_filters_results(self):
        results = suggest_retry_policies(max_interval_minutes=10)
        assert all(r.interval_minutes <= 10 for r in results)

    def test_min_interval_filters_results(self):
        results = suggest_retry_policies(min_interval_minutes=30)
        assert all(r.interval_minutes >= 30 for r in results)

    def test_exact_interval_match(self):
        results = suggest_retry_policies(
            min_interval_minutes=5, max_interval_minutes=5
        )
        assert len(results) == 1
        assert results[0].interval_minutes == 5

    def test_invalid_min_raises(self):
        with pytest.raises(ValueError, match="min_interval_minutes"):
            suggest_retry_policies(min_interval_minutes=0)

    def test_inverted_bounds_raises(self):
        with pytest.raises(ValueError, match="max_interval_minutes"):
            suggest_retry_policies(
                min_interval_minutes=60, max_interval_minutes=5
            )

    def test_all_expressions_are_valid(self):
        from crontab_gen.expression import is_valid

        for rp in suggest_retry_policies():
            assert is_valid(rp.expression), f"Invalid: {rp.expression}"

    def test_descriptions_are_non_empty(self):
        for rp in suggest_retry_policies():
            assert rp.description.strip() != ""

    def test_jitter_notes_are_non_empty(self):
        for rp in suggest_retry_policies():
            assert rp.jitter_note.strip() != ""
