"""Tests for crontab_gen.note module."""
from __future__ import annotations

import pytest
from pathlib import Path

from crontab_gen.note import (
    NoteEntry,
    add_note,
    list_notes,
    remove_note,
    update_note,
)


@pytest.fixture
def note_file(tmp_path: Path) -> Path:
    return tmp_path / "notes.json"


class TestNoteEntry:
    def test_to_dict_roundtrip(self):
        e = NoteEntry(expression="* * * * *", text="runs every minute")
        d = e.to_dict()
        restored = NoteEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.text == e.text

    def test_updated_at_excluded_when_none(self):
        e = NoteEntry(expression="0 * * * *", text="hourly")
        assert "updated_at" not in e.to_dict()

    def test_updated_at_included_when_set(self):
        e = NoteEntry(expression="0 * * * *", text="hourly", updated_at="2024-01-01T00:00:00+00:00")
        assert "updated_at" in e.to_dict()

    def test_created_at_is_set(self):
        e = NoteEntry(expression="* * * * *", text="test")
        assert e.created_at != ""


class TestAddNote:
    def test_add_returns_entry(self, note_file):
        e = add_note("* * * * *", "hello", path=note_file)
        assert isinstance(e, NoteEntry)
        assert e.text == "hello"

    def test_add_persists(self, note_file):
        add_note("* * * * *", "persisted", path=note_file)
        entries = list_notes(path=note_file)
        assert len(entries) == 1
        assert entries[0].text == "persisted"

    def test_multiple_notes_same_expression(self, note_file):
        add_note("* * * * *", "first", path=note_file)
        add_note("* * * * *", "second", path=note_file)
        entries = list_notes("* * * * *", path=note_file)
        assert len(entries) == 2


class TestListNotes:
    def test_filter_by_expression(self, note_file):
        add_note("* * * * *", "note A", path=note_file)
        add_note("0 * * * *", "note B", path=note_file)
        results = list_notes("* * * * *", path=note_file)
        assert all(e.expression == "* * * * *" for e in results)
        assert len(results) == 1

    def test_list_all_when_no_filter(self, note_file):
        add_note("* * * * *", "a", path=note_file)
        add_note("0 * * * *", "b", path=note_file)
        assert len(list_notes(path=note_file)) == 2

    def test_empty_when_no_notes(self, note_file):
        assert list_notes(path=note_file) == []


class TestRemoveNote:
    def test_remove_reduces_count(self, note_file):
        add_note("* * * * *", "to remove", path=note_file)
        assert remove_note("* * * * *", 0, path=note_file) is True
        assert list_notes(path=note_file) == []

    def test_remove_invalid_index_returns_false(self, note_file):
        add_note("* * * * *", "only", path=note_file)
        assert remove_note("* * * * *", 5, path=note_file) is False


class TestUpdateNote:
    def test_update_changes_text(self, note_file):
        add_note("* * * * *", "old", path=note_file)
        updated = update_note("* * * * *", 0, "new", path=note_file)
        assert updated is not None
        assert updated.text == "new"

    def test_update_sets_updated_at(self, note_file):
        add_note("* * * * *", "original", path=note_file)
        updated = update_note("* * * * *", 0, "changed", path=note_file)
        assert updated.updated_at is not None

    def test_update_invalid_index_returns_none(self, note_file):
        add_note("* * * * *", "only", path=note_file)
        assert update_note("* * * * *", 9, "x", path=note_file) is None
