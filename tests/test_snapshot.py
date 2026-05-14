"""Tests for crontab_gen.snapshot module."""
import pytest
from unittest.mock import patch

from crontab_gen.snapshot import SnapshotEntry, add_snapshot, list_snapshots, clear_snapshots


@pytest.fixture
def snap_file(tmp_path):
    return str(tmp_path / "snapshots.json")


class TestSnapshotEntry:
    def test_to_dict_roundtrip(self):
        e = SnapshotEntry(expression="0 * * * *", label="hourly", created_at="2024-01-01T00:00:00+00:00")
        d = e.to_dict()
        restored = SnapshotEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.label == e.label
        assert restored.created_at == e.created_at

    def test_label_excluded_when_none(self):
        e = SnapshotEntry(expression="* * * * *")
        assert "label" not in e.to_dict()

    def test_label_included_when_set(self):
        e = SnapshotEntry(expression="* * * * *", label="every-min")
        assert e.to_dict()["label"] == "every-min"

    def test_created_at_is_set_automatically(self):
        e = SnapshotEntry(expression="* * * * *")
        assert e.created_at is not None
        assert "T" in e.created_at


class TestAddSnapshot:
    def test_returns_entry(self, snap_file):
        entry = add_snapshot("0 12 * * *", path=snap_file)
        assert entry.expression == "0 12 * * *"

    def test_entry_persisted(self, snap_file):
        add_snapshot("0 12 * * *", path=snap_file)
        entries = list_snapshots(path=snap_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 12 * * *"

    def test_multiple_entries_accumulate(self, snap_file):
        add_snapshot("0 1 * * *", path=snap_file)
        add_snapshot("0 2 * * *", path=snap_file)
        entries = list_snapshots(path=snap_file)
        assert len(entries) == 2

    def test_label_stored(self, snap_file):
        add_snapshot("@daily", label="daily-job", path=snap_file)
        entries = list_snapshots(path=snap_file)
        assert entries[0].label == "daily-job"


class TestListSnapshots:
    def test_empty_when_no_file(self, snap_file):
        entries = list_snapshots(path=snap_file)
        assert entries == []

    def test_returns_list_of_entries(self, snap_file):
        add_snapshot("* * * * *", path=snap_file)
        result = list_snapshots(path=snap_file)
        assert isinstance(result, list)
        assert all(isinstance(e, SnapshotEntry) for e in result)


class TestClearSnapshots:
    def test_returns_count(self, snap_file):
        add_snapshot("* * * * *", path=snap_file)
        add_snapshot("0 0 * * *", path=snap_file)
        count = clear_snapshots(path=snap_file)
        assert count == 2

    def test_empties_storage(self, snap_file):
        add_snapshot("* * * * *", path=snap_file)
        clear_snapshots(path=snap_file)
        assert list_snapshots(path=snap_file) == []

    def test_clear_empty_returns_zero(self, snap_file):
        assert clear_snapshots(path=snap_file) == 0
