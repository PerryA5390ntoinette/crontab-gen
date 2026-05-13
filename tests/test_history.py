"""Tests for crontab_gen.history module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_gen.history import (
    MAX_HISTORY,
    HistoryEntry,
    add_entry,
    clear_history,
    get_history,
)


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


class TestHistoryEntry:
    def test_to_dict_roundtrip(self):
        entry = HistoryEntry(expression="0 * * * *", description="hourly")
        restored = HistoryEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.description == entry.description

    def test_created_at_is_set(self):
        entry = HistoryEntry(expression="* * * * *", description="")
        assert entry.created_at != ""


class TestAddEntry:
    def test_adds_to_empty_file(self, hist_file):
        add_entry("* * * * *", "every minute", path=hist_file)
        entries = get_history(path=hist_file)
        assert len(entries) == 1
        assert entries[0].expression == "* * * * *"

    def test_newest_first(self, hist_file):
        add_entry("0 * * * *", "hourly", path=hist_file)
        add_entry("0 0 * * *", "daily", path=hist_file)
        entries = get_history(path=hist_file)
        assert entries[0].expression == "0 0 * * *"

    def test_max_history_respected(self, hist_file):
        for i in range(MAX_HISTORY + 5):
            add_entry(f"{i} * * * *", f"entry {i}", path=hist_file)
        entries = get_history(path=hist_file)
        assert len(entries) == MAX_HISTORY

    def test_returns_entry(self, hist_file):
        entry = add_entry("5 4 * * *", "custom", path=hist_file)
        assert isinstance(entry, HistoryEntry)
        assert entry.expression == "5 4 * * *"


class TestGetHistory:
    def test_returns_empty_list_when_no_file(self, tmp_path):
        missing = tmp_path / "nonexistent.json"
        assert get_history(path=missing) == []

    def test_limit_parameter(self, hist_file):
        for i in range(10):
            add_entry(f"{i} * * * *", "", path=hist_file)
        entries = get_history(limit=3, path=hist_file)
        assert len(entries) == 3

    def test_corrupted_file_returns_empty(self, hist_file):
        hist_file.write_text("not valid json")
        assert get_history(path=hist_file) == []


class TestClearHistory:
    def test_clears_all_entries(self, hist_file):
        add_entry("* * * * *", "a", path=hist_file)
        add_entry("0 * * * *", "b", path=hist_file)
        count = clear_history(path=hist_file)
        assert count == 2
        assert get_history(path=hist_file) == []

    def test_clear_empty_returns_zero(self, hist_file):
        assert clear_history(path=hist_file) == 0
