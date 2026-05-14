"""Tests for crontab_gen.compare."""

import pytest

from crontab_gen.compare import compare, CompareResult, FieldComparison, FIELD_NAMES


class TestCompareIdentical:
    def test_identical_expressions_are_identical(self):
        result = compare("* * * * *", "* * * * *")
        assert result.identical is True

    def test_identical_has_no_changed_fields(self):
        result = compare("0 12 * * *", "0 12 * * *")
        assert result.changed_fields == []

    def test_all_fields_same(self):
        result = compare("5 4 3 2 1", "5 4 3 2 1")
        assert all(f.same for f in result.fields)


class TestCompareDifferent:
    def test_minute_differs(self):
        result = compare("0 * * * *", "5 * * * *")
        assert result.identical is False

    def test_changed_fields_contains_minute(self):
        result = compare("0 * * * *", "5 * * * *")
        names = [f.name for f in result.changed_fields]
        assert "minute" in names

    def test_multiple_fields_differ(self):
        result = compare("0 12 * * *", "30 6 * * *")
        assert len(result.changed_fields) == 2

    def test_changed_field_names_correct(self):
        result = compare("0 12 * * *", "30 6 * * *")
        names = {f.name for f in result.changed_fields}
        assert names == {"minute", "hour"}


class TestCompareFields:
    def test_returns_five_fields(self):
        result = compare("* * * * *", "* * * * *")
        assert len(result.fields) == 5

    def test_field_names_match_expected(self):
        result = compare("* * * * *", "* * * * *")
        names = [f.name for f in result.fields]
        assert names == FIELD_NAMES

    def test_field_left_value(self):
        result = compare("0 12 * * *", "0 6 * * *")
        hour_field = next(f for f in result.fields if f.name == "hour")
        assert hour_field.left == "12"

    def test_field_right_value(self):
        result = compare("0 12 * * *", "0 6 * * *")
        hour_field = next(f for f in result.fields if f.name == "hour")
        assert hour_field.right == "6"


class TestCompareValidation:
    def test_invalid_left_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            compare("not valid", "* * * * *")

    def test_invalid_right_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            compare("* * * * *", "bad expr")

    def test_both_invalid_raises(self):
        with pytest.raises(ValueError):
            compare("bad", "also bad")


class TestCompareStr:
    def test_str_contains_left_expression(self):
        result = compare("* * * * *", "0 12 * * *")
        assert "* * * * *" in str(result)

    def test_str_contains_right_expression(self):
        result = compare("* * * * *", "0 12 * * *")
        assert "0 12 * * *" in str(result)

    def test_str_identical_note(self):
        result = compare("* * * * *", "* * * * *")
        assert "identical" in str(result).lower()

    def test_str_differ_count(self):
        result = compare("0 12 * * *", "30 6 * * *")
        assert "2" in str(result)
