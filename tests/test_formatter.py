"""Tests for the formatter module."""

import pytest

from crontab_gen.formatter import (
    format_preset_row,
    format_preset_table,
    format_preset_detail,
    format_categories,
)
from crontab_gen.presets import get_preset, CronPreset


class TestFormatPresetRow:
    def test_contains_name(self):
        preset = get_preset("hourly")
        row = format_preset_row(preset)
        assert "hourly" in row

    def test_contains_expression(self):
        preset = get_preset("hourly")
        row = format_preset_row(preset)
        assert "0 * * * *" in row

    def test_contains_alias_when_present(self):
        preset = get_preset("hourly")
        row = format_preset_row(preset)
        assert "@hourly" in row

    def test_no_alias_shows_empty(self):
        preset = CronPreset(
            name="test",
            expression="1 2 3 4 5",
            description="test preset",
            category="test",
        )
        row = format_preset_row(preset)
        assert "test" in row
        assert "1 2 3 4 5" in row


class TestFormatPresetTable:
    def test_returns_string(self):
        result = format_preset_table()
        assert isinstance(result, str)

    def test_contains_header(self):
        result = format_preset_table()
        assert "NAME" in result
        assert "EXPRESSION" in result

    def test_filtered_by_category(self):
        result = format_preset_table("daily")
        assert "daily" in result.lower()

    def test_unknown_category_returns_message(self):
        result = format_preset_table("nope")
        assert "No presets found" in result


class TestFormatPresetDetail:
    def test_contains_all_fields(self):
        preset = get_preset("daily")
        detail = format_preset_detail(preset)
        assert "daily" in detail
        assert "0 0 * * *" in detail
        assert "midnight" in detail.lower()
        assert "@daily" in detail

    def test_no_alias_line_when_absent(self):
        preset = CronPreset(
            name="custom",
            expression="5 4 * * *",
            description="custom job",
            category="daily",
        )
        detail = format_preset_detail(preset)
        assert "Alias" not in detail


class TestFormatCategories:
    def test_returns_string(self):
        result = format_categories()
        assert isinstance(result, str)

    def test_contains_known_categories(self):
        result = format_categories()
        assert "frequent" in result
        assert "daily" in result
