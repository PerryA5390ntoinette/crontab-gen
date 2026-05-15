"""Tests for crontab_gen.priority."""
import json
import pytest
from pathlib import Path

from crontab_gen.priority import (
    PriorityEntry,
    add_priority,
    remove_priority,
    list_priorities,
    LEVELS,
)


@pytest.fixture
def pri_file(tmp_path) -> Path:
    return tmp_path / "priorities.json"


class TestPriorityEntry:
    def test_to_dict_roundtrip(self):
        e = PriorityEntry(expression="* * * * *", level="high", label="every minute")
        d = e.to_dict()
        e2 = PriorityEntry.from_dict(d)
        assert e2.expression == e.expression
        assert e2.level == e.level
        assert e2.label == e.label

    def test_label_excluded_when_none(self):
        e = PriorityEntry(expression="0 * * * *", level="low")
        assert "label" not in e.to_dict()

    def test_label_included_when_set(self):
        e = PriorityEntry(expression="0 * * * *", level="low", label="hourly")
        assert e.to_dict()["label"] == "hourly"

    def test_created_at_is_set(self):
        e = PriorityEntry(expression="0 * * * *", level="medium")
        assert e.created_at is not None
        assert "T" in e.created_at


class TestAddPriority:
    def test_add_creates_file(self, pri_file):
        add_priority("* * * * *", "low", path=pri_file)
        assert pri_file.exists()

    def test_add_persists_entry(self, pri_file):
        add_priority("0 6 * * *", "high", label="morning", path=pri_file)
        entries = list_priorities(path=pri_file)
        assert len(entries) == 1
        assert entries[0].level == "high"
        assert entries[0].label == "morning"

    def test_invalid_level_raises(self, pri_file):
        with pytest.raises(ValueError, match="level must be one of"):
            add_priority("* * * * *", "urgent", path=pri_file)

    def test_multiple_entries(self, pri_file):
        add_priority("* * * * *", "low", path=pri_file)
        add_priority("0 * * * *", "high", path=pri_file)
        assert len(list_priorities(path=pri_file)) == 2


class TestRemovePriority:
    def test_remove_returns_true(self, pri_file):
        add_priority("* * * * *", "low", path=pri_file)
        assert remove_priority("* * * * *", path=pri_file) is True

    def test_remove_reduces_count(self, pri_file):
        add_priority("* * * * *", "low", path=pri_file)
        add_priority("0 * * * *", "high", path=pri_file)
        remove_priority("* * * * *", path=pri_file)
        assert len(list_priorities(path=pri_file)) == 1

    def test_remove_missing_returns_false(self, pri_file):
        assert remove_priority("* * * * *", path=pri_file) is False


class TestListPriorities:
    def test_filter_by_level(self, pri_file):
        add_priority("* * * * *", "low", path=pri_file)
        add_priority("0 * * * *", "high", path=pri_file)
        result = list_priorities(level="high", path=pri_file)
        assert len(result) == 1
        assert result[0].level == "high"

    def test_no_filter_returns_all(self, pri_file):
        for lvl in LEVELS:
            add_priority(f"0 {LEVELS.index(lvl)} * * *", lvl, path=pri_file)
        assert len(list_priorities(path=pri_file)) == len(LEVELS)
