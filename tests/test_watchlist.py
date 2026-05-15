"""Tests for crontab_gen.watchlist."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_gen.watchlist import (
    WatchEntry,
    add_entry,
    clear_entries,
    list_entries,
    remove_entry,
)


@pytest.fixture()
def watch_file(tmp_path: Path) -> Path:
    return tmp_path / "watchlist.json"


class TestWatchEntry:
    def test_to_dict_roundtrip(self):
        entry = WatchEntry(expression="0 * * * *", label="hourly")
        restored = WatchEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.label == entry.label
        assert restored.created_at == entry.created_at

    def test_label_excluded_when_none(self):
        entry = WatchEntry(expression="* * * * *")
        assert "label" not in entry.to_dict()

    def test_label_included_when_set(self):
        entry = WatchEntry(expression="* * * * *", label="every minute")
        assert entry.to_dict()["label"] == "every minute"

    def test_created_at_is_set(self):
        entry = WatchEntry(expression="5 4 * * *")
        assert entry.created_at is not None
        assert len(entry.created_at) > 0


class TestAddEntry:
    def test_adds_entry(self, watch_file: Path):
        add_entry("0 12 * * *", path=watch_file)
        entries = list_entries(path=watch_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 12 * * *"

    def test_adds_label(self, watch_file: Path):
        add_entry("0 6 * * *", label="morning", path=watch_file)
        entries = list_entries(path=watch_file)
        assert entries[0].label == "morning"

    def test_multiple_entries(self, watch_file: Path):
        add_entry("0 1 * * *", path=watch_file)
        add_entry("0 2 * * *", path=watch_file)
        entries = list_entries(path=watch_file)
        assert len(entries) == 2

    def test_returns_entry(self, watch_file: Path):
        result = add_entry("*/5 * * * *", path=watch_file)
        assert isinstance(result, WatchEntry)
        assert result.expression == "*/5 * * * *"


class TestRemoveEntry:
    def test_removes_matching_expression(self, watch_file: Path):
        add_entry("0 0 * * *", path=watch_file)
        removed = remove_entry("0 0 * * *", path=watch_file)
        assert removed is True
        assert list_entries(path=watch_file) == []

    def test_returns_false_when_not_found(self, watch_file: Path):
        removed = remove_entry("0 0 * * *", path=watch_file)
        assert removed is False

    def test_only_removes_matching(self, watch_file: Path):
        add_entry("0 1 * * *", path=watch_file)
        add_entry("0 2 * * *", path=watch_file)
        remove_entry("0 1 * * *", path=watch_file)
        entries = list_entries(path=watch_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 2 * * *"


class TestClearEntries:
    def test_clears_all(self, watch_file: Path):
        add_entry("* * * * *", path=watch_file)
        add_entry("0 0 * * *", path=watch_file)
        count = clear_entries(path=watch_file)
        assert count == 2
        assert list_entries(path=watch_file) == []

    def test_clear_empty_returns_zero(self, watch_file: Path):
        assert clear_entries(path=watch_file) == 0
