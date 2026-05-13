"""Tests for crontab_gen.diff module."""

import pytest

from crontab_gen.diff import diff_expressions, ExpressionDiff, FieldDiff
from crontab_gen.expression import CronField


class TestDiffExpressions:
    def test_identical_expressions_no_changes(self):
        result = diff_expressions("0 9 * * 1", "0 9 * * 1")
        assert not result.has_changes

    def test_different_minute_detected(self):
        result = diff_expressions("0 9 * * 1", "30 9 * * 1")
        assert result.has_changes
        changed = result.changed_fields
        assert len(changed) == 1
        assert changed[0].field == CronField.MINUTE

    def test_multiple_fields_changed(self):
        result = diff_expressions("0 9 * * 1", "0 10 1 * *")
        names = {d.field for d in result.changed_fields}
        assert CronField.HOUR in names
        assert CronField.DAY_OF_MONTH in names
        assert CronField.DAY_OF_WEEK in names

    def test_all_fields_present_in_diff(self):
        result = diff_expressions("* * * * *", "* * * * *")
        assert len(result.field_diffs) == 5

    def test_field_values_stored(self):
        result = diff_expressions("5 10 * * *", "5 12 * * *")
        hour_diff = next(d for d in result.field_diffs if d.field == CronField.HOUR)
        assert hour_diff.left == "10"
        assert hour_diff.right == "12"

    def test_explanations_populated(self):
        result = diff_expressions("0 9 * * 1", "0 10 * * 1")
        hour_diff = next(d for d in result.field_diffs if d.field == CronField.HOUR)
        assert hour_diff.left_explanation
        assert hour_diff.right_explanation

    def test_invalid_left_raises(self):
        with pytest.raises(ValueError, match="left"):
            diff_expressions("99 * * * *", "* * * * *")

    def test_invalid_right_raises(self):
        with pytest.raises(ValueError, match="right"):
            diff_expressions("* * * * *", "* * * * 99")

    def test_returns_expression_diff_type(self):
        result = diff_expressions("* * * * *", "0 * * * *")
        assert isinstance(result, ExpressionDiff)

    def test_changed_fields_subset_of_all(self):
        result = diff_expressions("0 9 * * *", "0 10 * * *")
        assert len(result.changed_fields) <= len(result.field_diffs)
