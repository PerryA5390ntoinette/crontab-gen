"""Tests for cron expression parsing, validation, and explanation."""

import pytest
from crontab_gen.expression import CronExpression, CronField
from crontab_gen.explainer import explain


class TestCronExpressionValidation:
    def test_valid_simple(self):
        valid, errors = CronExpression("* * * * *").validate()
        assert valid
        assert errors == []

    def test_valid_specific_time(self):
        valid, errors = CronExpression("30 8 * * 1").validate()
        assert valid

    def test_valid_ranges(self):
        valid, errors = CronExpression("0 9-17 * * 1-5").validate()
        assert valid

    def test_valid_step(self):
        valid, errors = CronExpression("*/15 * * * *").validate()
        assert valid

    def test_valid_comma_list(self):
        valid, errors = CronExpression("0 0 1,15 * *").validate()
        assert valid

    def test_valid_month_alias(self):
        valid, errors = CronExpression("0 0 1 jan *").validate()
        assert valid

    def test_valid_dow_alias(self):
        valid, errors = CronExpression("0 9 * * mon").validate()
        assert valid

    def test_invalid_field_count_too_few(self):
        valid, errors = CronExpression("* * *").validate()
        assert not valid
        assert any("5 fields" in e for e in errors)

    def test_invalid_minute_out_of_range(self):
        valid, errors = CronExpression("60 * * * *").validate()
        assert not valid
        assert any("minute" in e for e in errors)

    def test_invalid_hour_out_of_range(self):
        valid, errors = CronExpression("0 25 * * *").validate()
        assert not valid

    def test_invalid_range_start_gt_end(self):
        valid, errors = CronExpression("0 17-9 * * *").validate()
        assert not valid

    def test_invalid_step_zero(self):
        valid, errors = CronExpression("*/0 * * * *").validate()
        assert not valid

    def test_fields_returns_five(self):
        fields = CronExpression("0 12 * * *").fields()
        assert len(fields) == 5
        assert fields[0].name == "minute"
        assert fields[1].name == "hour"


class TestExplainer:
    def test_every_minute(self):
        result = explain("* * * * *")
        assert "Every minute" in result

    def test_specific_time(self):
        result = explain("30 8 * * *")
        assert "30" in result
        assert "8" in result

    def test_with_month(self):
        result = explain("0 0 1 1 *")
        assert "Jan" in result

    def test_with_dow(self):
        result = explain("0 9 * * 1")
        assert "Mon" in result

    def test_invalid_expression(self):
        result = explain("invalid")
        assert "Invalid" in result

    def test_step_expression(self):
        result = explain("*/15 * * * *")
        assert "15" in result
