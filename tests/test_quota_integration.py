"""Integration tests for the quota module against the expression engine."""
from __future__ import annotations

from datetime import datetime

import pytest

from crontab_gen.quota import check_quota
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain

REF = datetime(2024, 3, 1, 0, 0)

EXPRESSIONS = [
    ("* * * * *", 1440, 24),   # every minute — 1440 fires per day
    ("0 * * * *", 24, 24),     # hourly
    ("0 0 * * *", 1, 24),      # daily
    ("*/5 * * * *", 288, 24),  # every 5 minutes
    ("0 9-17 * * 1-5", 9, 24), # business hours Mon-Fri (9 firings on a Monday)
]


class TestQuotaIntegration:
    @pytest.mark.parametrize("expr,_,__", EXPRESSIONS)
    def test_expression_is_valid(self, expr, _, __):
        assert is_valid(expr)

    @pytest.mark.parametrize("expr,_,__", EXPRESSIONS)
    def test_expression_is_explainable(self, expr, _, __):
        result = explain(expr)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_every_minute_actual_count_in_one_hour(self):
        result = check_quota("* * * * *", limit=9999, window_hours=1, reference=REF)
        assert result.actual == 60

    def test_hourly_actual_count_in_24h(self):
        result = check_quota("0 * * * *", limit=9999, window_hours=24, reference=REF)
        assert result.actual == 24

    def test_daily_actual_count_in_48h(self):
        result = check_quota("0 0 * * *", limit=9999, window_hours=48, reference=REF)
        assert result.actual == 2

    def test_quota_ok_flag_reflects_limit(self):
        r_ok = check_quota("0 * * * *", limit=24, window_hours=24, reference=REF)
        r_fail = check_quota("0 * * * *", limit=23, window_hours=24, reference=REF)
        assert r_ok.ok is True
        assert r_fail.ok is False

    def test_warnings_list_populated_on_breach(self):
        result = check_quota("* * * * *", limit=1, window_hours=1, reference=REF)
        assert len(result.warnings) == 1
        assert result.warnings[0].expression == "* * * * *"
