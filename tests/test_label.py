"""Tests for crontab_gen.label module."""
import pytest

from crontab_gen.label import (
    LabelEntry,
    add_label,
    find_label,
    list_labels,
    remove_label,
)


@pytest.fixture
def label_file(tmp_path):
    return str(tmp_path / "labels.json")


class TestLabelEntry:
    def test_to_dict_roundtrip(self):
        entry = LabelEntry(expression="* * * * *", label="every minute")
        restored = LabelEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.label == entry.label
        assert restored.created_at == entry.created_at

    def test_created_at_is_set(self):
        entry = LabelEntry(expression="0 * * * *", label="hourly")
        assert entry.created_at is not None
        assert len(entry.created_at) > 0


class TestAddLabel:
    def test_add_returns_entry(self, label_file):
        entry = add_label("* * * * *", "every minute", path=label_file)
        assert entry.expression == "* * * * *"
        assert entry.label == "every minute"

    def test_add_persists(self, label_file):
        add_label("0 0 * * *", "daily", path=label_file)
        entries = list_labels(path=label_file)
        assert len(entries) == 1
        assert entries[0].label == "daily"

    def test_multiple_labels(self, label_file):
        add_label("* * * * *", "every minute", path=label_file)
        add_label("0 * * * *", "hourly", path=label_file)
        entries = list_labels(path=label_file)
        assert len(entries) == 2


class TestRemoveLabel:
    def test_remove_existing(self, label_file):
        add_label("* * * * *", "every minute", path=label_file)
        result = remove_label("* * * * *", path=label_file)
        assert result is True
        assert list_labels(path=label_file) == []

    def test_remove_nonexistent_returns_false(self, label_file):
        result = remove_label("* * * * *", path=label_file)
        assert result is False

    def test_remove_only_matching(self, label_file):
        add_label("* * * * *", "every minute", path=label_file)
        add_label("0 * * * *", "hourly", path=label_file)
        remove_label("* * * * *", path=label_file)
        entries = list_labels(path=label_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 * * * *"


class TestFindLabel:
    def test_find_existing(self, label_file):
        add_label("0 0 * * *", "midnight", path=label_file)
        entry = find_label("0 0 * * *", path=label_file)
        assert entry is not None
        assert entry.label == "midnight"

    def test_find_nonexistent_returns_none(self, label_file):
        entry = find_label("0 0 * * *", path=label_file)
        assert entry is None


class TestListLabels:
    def test_empty_returns_empty_list(self, label_file):
        assert list_labels(path=label_file) == []

    def test_returns_all_entries(self, label_file):
        add_label("* * * * *", "a", path=label_file)
        add_label("0 * * * *", "b", path=label_file)
        assert len(list_labels(path=label_file)) == 2
