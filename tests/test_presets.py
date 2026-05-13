"""Tests for the presets module."""

import pytest

from crontab_gen.presets import (
    get_preset,
    list_presets,
    categories,
    PRESETS,
    CronPreset,
)


class TestGetPreset:
    def test_get_by_name(self):
        preset = get_preset("hourly")
        assert preset is not None
        assert preset.expression == "0 * * * *"

    def test_get_by_alias(self):
        preset = get_preset("@hourly")
        assert preset is not None
        assert preset.name == "hourly"

    def test_get_unknown_returns_none(self):
        assert get_preset("does-not-exist") is None

    def test_case_insensitive_name(self):
        preset = get_preset("DAILY")
        assert preset is not None
        assert preset.name == "daily"

    def test_every_preset_has_required_fields(self):
        for p in PRESETS:
            assert p.name
            assert p.expression
            assert p.description
            assert p.category


class TestListPresets:
    def test_list_all(self):
        result = list_presets()
        assert len(result) == len(PRESETS)

    def test_list_by_category(self):
        frequent = list_presets("frequent")
        assert len(frequent) > 0
        for p in frequent:
            assert p.category == "frequent"

    def test_list_unknown_category_empty(self):
        result = list_presets("nonexistent")
        assert result == []

    def test_list_returns_copies_not_mutating(self):
        a = list_presets()
        b = list_presets()
        assert a == b


class TestCategories:
    def test_returns_list(self):
        cats = categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_no_duplicates(self):
        cats = categories()
        assert len(cats) == len(set(cats))

    def test_known_categories_present(self):
        cats = categories()
        assert "frequent" in cats
        assert "daily" in cats
        assert "weekly" in cats
        assert "monthly" in cats
        assert "yearly" in cats
