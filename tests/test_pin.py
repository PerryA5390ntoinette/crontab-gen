"""Tests for crontab_gen/pin.py"""
import json
import pytest
from pathlib import Path
from crontab_gen.pin import PinEntry, add_pin, remove_pin, list_pins, clear_pins


@pytest.fixture
def pin_file(tmp_path):
    return tmp_path / "pins.json"


class TestPinEntry:
    def test_to_dict_roundtrip(self):
        e = PinEntry(expression="0 9 * * 1", label="weekly", pinned_at="2024-01-01T00:00:00+00:00")
        d = e.to_dict()
        restored = PinEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.label == e.label
        assert restored.pinned_at == e.pinned_at

    def test_label_excluded_when_none(self):
        e = PinEntry(expression="* * * * *")
        assert "label" not in e.to_dict()

    def test_label_included_when_set(self):
        e = PinEntry(expression="* * * * *", label="every minute")
        assert e.to_dict()["label"] == "every minute"

    def test_pinned_at_is_set(self):
        e = PinEntry(expression="0 0 * * *")
        assert e.pinned_at is not None
        assert "T" in e.pinned_at


class TestAddPin:
    def test_adds_entry(self, pin_file):
        add_pin("0 9 * * 1", path=pin_file)
        entries = list_pins(path=pin_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 9 * * 1"

    def test_adds_label(self, pin_file):
        add_pin("0 9 * * 1", label="standup", path=pin_file)
        entries = list_pins(path=pin_file)
        assert entries[0].label == "standup"

    def test_multiple_pins(self, pin_file):
        add_pin("* * * * *", path=pin_file)
        add_pin("0 0 * * *", path=pin_file)
        entries = list_pins(path=pin_file)
        assert len(entries) == 2

    def test_returns_entry(self, pin_file):
        entry = add_pin("*/5 * * * *", path=pin_file)
        assert isinstance(entry, PinEntry)
        assert entry.expression == "*/5 * * * *"


class TestRemovePin:
    def test_removes_existing(self, pin_file):
        add_pin("0 9 * * 1", path=pin_file)
        result = remove_pin("0 9 * * 1", path=pin_file)
        assert result is True
        assert list_pins(path=pin_file) == []

    def test_returns_false_when_not_found(self, pin_file):
        result = remove_pin("0 9 * * 1", path=pin_file)
        assert result is False

    def test_removes_only_matching(self, pin_file):
        add_pin("* * * * *", path=pin_file)
        add_pin("0 0 * * *", path=pin_file)
        remove_pin("* * * * *", path=pin_file)
        entries = list_pins(path=pin_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 0 * * *"


class TestClearPins:
    def test_clears_all(self, pin_file):
        add_pin("* * * * *", path=pin_file)
        add_pin("0 0 * * *", path=pin_file)
        count = clear_pins(path=pin_file)
        assert count == 2
        assert list_pins(path=pin_file) == []

    def test_clear_empty_returns_zero(self, pin_file):
        assert clear_pins(path=pin_file) == 0
