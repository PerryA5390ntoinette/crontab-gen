"""Tests for crontab_gen.annotate module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_gen.annotate import (
    AnnotationEntry,
    add_annotation,
    get_annotation,
    list_annotations,
    remove_annotation,
)


@pytest.fixture
def ann_file(tmp_path: Path) -> Path:
    return tmp_path / "annotations.json"


class TestAnnotationEntry:
    def test_to_dict_roundtrip(self):
        e = AnnotationEntry(expression="* * * * *", note="every minute")
        d = e.to_dict()
        restored = AnnotationEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.note == e.note
        assert restored.created_at == e.created_at

    def test_updated_at_excluded_when_none(self):
        e = AnnotationEntry(expression="0 * * * *", note="hourly")
        assert "updated_at" not in e.to_dict()

    def test_updated_at_included_when_set(self):
        e = AnnotationEntry(expression="0 * * * *", note="hourly", updated_at="2024-01-01T00:00:00+00:00")
        assert "updated_at" in e.to_dict()

    def test_created_at_is_set_automatically(self):
        e = AnnotationEntry(expression="* * * * *", note="test")
        assert e.created_at != ""


class TestAddAnnotation:
    def test_adds_new_entry(self, ann_file):
        add_annotation("* * * * *", "every minute", path=ann_file)
        entries = list_annotations(path=ann_file)
        assert len(entries) == 1
        assert entries[0].expression == "* * * * *"
        assert entries[0].note == "every minute"

    def test_updates_existing_entry(self, ann_file):
        add_annotation("* * * * *", "original", path=ann_file)
        add_annotation("* * * * *", "updated", path=ann_file)
        entries = list_annotations(path=ann_file)
        assert len(entries) == 1
        assert entries[0].note == "updated"
        assert entries[0].updated_at is not None

    def test_multiple_expressions_stored(self, ann_file):
        add_annotation("* * * * *", "note1", path=ann_file)
        add_annotation("0 * * * *", "note2", path=ann_file)
        entries = list_annotations(path=ann_file)
        assert len(entries) == 2


class TestGetAnnotation:
    def test_returns_entry_when_found(self, ann_file):
        add_annotation("0 0 * * *", "daily", path=ann_file)
        result = get_annotation("0 0 * * *", path=ann_file)
        assert result is not None
        assert result.note == "daily"

    def test_returns_none_when_not_found(self, ann_file):
        result = get_annotation("0 0 * * *", path=ann_file)
        assert result is None


class TestRemoveAnnotation:
    def test_removes_existing_entry(self, ann_file):
        add_annotation("* * * * *", "note", path=ann_file)
        removed = remove_annotation("* * * * *", path=ann_file)
        assert removed is True
        assert list_annotations(path=ann_file) == []

    def test_returns_false_when_not_found(self, ann_file):
        removed = remove_annotation("* * * * *", path=ann_file)
        assert removed is False

    def test_only_removes_target(self, ann_file):
        add_annotation("* * * * *", "a", path=ann_file)
        add_annotation("0 * * * *", "b", path=ann_file)
        remove_annotation("* * * * *", path=ann_file)
        remaining = list_annotations(path=ann_file)
        assert len(remaining) == 1
        assert remaining[0].expression == "0 * * * *"
