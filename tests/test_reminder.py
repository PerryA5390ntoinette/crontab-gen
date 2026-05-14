"""Tests for crontab_gen.reminder."""
import json
from pathlib import Path

import pytest

from crontab_gen.reminder import (
    ReminderEntry,
    add_reminder,
    clear_reminders,
    list_reminders,
)


@pytest.fixture
def rem_file(tmp_path) -> Path:
    return tmp_path / "reminders.json"


class TestReminderEntry:
    def test_to_dict_roundtrip(self):
        entry = ReminderEntry(expression="0 * * * *", message="Check logs")
        restored = ReminderEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.message == entry.message
        assert restored.created_at == entry.created_at

    def test_label_excluded_when_none(self):
        entry = ReminderEntry(expression="* * * * *", message="ping")
        assert "label" not in entry.to_dict()

    def test_label_included_when_set(self):
        entry = ReminderEntry(expression="* * * * *", message="ping", label="ops")
        assert entry.to_dict()["label"] == "ops"

    def test_created_at_is_set(self):
        entry = ReminderEntry(expression="* * * * *", message="test")
        assert entry.created_at is not None
        assert len(entry.created_at) > 0


class TestAddReminder:
    def test_creates_file(self, rem_file):
        add_reminder("* * * * *", "hello", path=rem_file)
        assert rem_file.exists()

    def test_entry_persisted(self, rem_file):
        add_reminder("0 9 * * 1", "standup", path=rem_file)
        entries = list_reminders(path=rem_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 9 * * 1"
        assert entries[0].message == "standup"

    def test_multiple_entries(self, rem_file):
        add_reminder("* * * * *", "first", path=rem_file)
        add_reminder("0 0 * * *", "second", path=rem_file)
        entries = list_reminders(path=rem_file)
        assert len(entries) == 2

    def test_label_stored(self, rem_file):
        add_reminder("5 4 * * *", "backup", label="infra", path=rem_file)
        entries = list_reminders(path=rem_file)
        assert entries[0].label == "infra"

    def test_returns_entry(self, rem_file):
        result = add_reminder("* * * * *", "msg", path=rem_file)
        assert isinstance(result, ReminderEntry)


class TestClearReminders:
    def test_clear_removes_all(self, rem_file):
        add_reminder("* * * * *", "a", path=rem_file)
        add_reminder("0 0 * * *", "b", path=rem_file)
        count = clear_reminders(path=rem_file)
        assert count == 2
        assert list_reminders(path=rem_file) == []

    def test_clear_empty_returns_zero(self, rem_file):
        count = clear_reminders(path=rem_file)
        assert count == 0


class TestListReminders:
    def test_empty_when_no_file(self, rem_file):
        assert list_reminders(path=rem_file) == []
