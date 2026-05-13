"""Tests for crontab_gen.tags module."""
from __future__ import annotations

import os
import pytest

from crontab_gen.tags import (
    TagEntry,
    add_tag,
    remove_tag,
    find_by_tag,
    list_tags,
)


@pytest.fixture
def tags_file(tmp_path):
    return str(tmp_path / "tags.json")


class TestTagEntry:
    def test_to_dict_roundtrip(self):
        entry = TagEntry(expression="0 * * * *", tags=["hourly"], note="every hour")
        restored = TagEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.tags == entry.tags
        assert restored.note == entry.note

    def test_defaults(self):
        entry = TagEntry(expression="* * * * *")
        assert entry.tags == []
        assert entry.note is None


class TestAddTag:
    def test_adds_new_entry(self, tags_file):
        entry = add_tag("0 9 * * 1", ["weekly"], path=tags_file)
        assert "weekly" in entry.tags

    def test_adds_note(self, tags_file):
        entry = add_tag("0 0 * * *", ["daily"], note="midnight", path=tags_file)
        assert entry.note == "midnight"

    def test_no_duplicate_tags(self, tags_file):
        add_tag("0 0 * * *", ["daily"], path=tags_file)
        entry = add_tag("0 0 * * *", ["daily"], path=tags_file)
        assert entry.tags.count("daily") == 1

    def test_multiple_tags(self, tags_file):
        entry = add_tag("*/5 * * * *", ["frequent", "monitoring"], path=tags_file)
        assert "frequent" in entry.tags
        assert "monitoring" in entry.tags

    def test_persists_to_file(self, tags_file):
        add_tag("0 12 * * *", ["noon"], path=tags_file)
        assert os.path.exists(tags_file)
        entries = list_tags(path=tags_file)
        assert any(e.expression == "0 12 * * *" for e in entries)


class TestRemoveTag:
    def test_removes_existing_tag(self, tags_file):
        add_tag("0 0 * * *", ["daily", "important"], path=tags_file)
        entry = remove_tag("0 0 * * *", ["important"], path=tags_file)
        assert "important" not in entry.tags
        assert "daily" in entry.tags

    def test_returns_none_for_unknown_expression(self, tags_file):
        result = remove_tag("9 9 9 9 9", ["nope"], path=tags_file)
        assert result is None


class TestFindByTag:
    def test_finds_matching_entries(self, tags_file):
        add_tag("0 0 * * *", ["daily"], path=tags_file)
        add_tag("0 0 * * 1", ["weekly"], path=tags_file)
        results = find_by_tag("daily", path=tags_file)
        assert len(results) == 1
        assert results[0].expression == "0 0 * * *"

    def test_returns_empty_for_unknown_tag(self, tags_file):
        add_tag("0 0 * * *", ["daily"], path=tags_file)
        assert find_by_tag("nope", path=tags_file) == []


class TestListTags:
    def test_empty_when_no_file(self, tags_file):
        assert list_tags(path=tags_file) == []

    def test_lists_all_entries(self, tags_file):
        add_tag("0 0 * * *", ["daily"], path=tags_file)
        add_tag("0 0 1 * *", ["monthly"], path=tags_file)
        assert len(list_tags(path=tags_file)) == 2
