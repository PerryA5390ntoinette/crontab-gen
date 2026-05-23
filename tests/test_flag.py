"""Tests for crontab_gen.flag module."""
import pytest
from crontab_gen.flag import (
    FlagEntry,
    VALID_FLAGS,
    add_flag,
    get_flag,
    list_flags,
    remove_flag,
)


@pytest.fixture
def flag_file(tmp_path):
    return str(tmp_path / "flags.json")


class TestFlagEntry:
    def test_to_dict_roundtrip(self):
        entry = FlagEntry(expression="* * * * *", flag="active", label="my job")
        restored = FlagEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.flag == entry.flag
        assert restored.label == entry.label
        assert restored.created_at == entry.created_at

    def test_label_excluded_when_none(self):
        entry = FlagEntry(expression="0 * * * *", flag="disabled")
        d = entry.to_dict()
        assert "label" not in d

    def test_label_included_when_set(self):
        entry = FlagEntry(expression="0 * * * *", flag="review", label="check this")
        d = entry.to_dict()
        assert d["label"] == "check this"

    def test_created_at_is_set(self):
        entry = FlagEntry(expression="* * * * *", flag="active")
        assert entry.created_at is not None
        assert len(entry.created_at) > 0


class TestAddFlag:
    def test_add_returns_entry(self, flag_file):
        entry = add_flag("* * * * *", "active", path=flag_file)
        assert isinstance(entry, FlagEntry)
        assert entry.flag == "active"

    def test_add_persists_entry(self, flag_file):
        add_flag("0 12 * * *", "review", path=flag_file)
        entries = list_flags(path=flag_file)
        assert len(entries) == 1
        assert entries[0].flag == "review"

    def test_add_replaces_existing_flag(self, flag_file):
        add_flag("* * * * *", "active", path=flag_file)
        add_flag("* * * * *", "disabled", path=flag_file)
        entries = list_flags(path=flag_file)
        assert len(entries) == 1
        assert entries[0].flag == "disabled"

    def test_invalid_flag_raises(self, flag_file):
        with pytest.raises(ValueError, match="Invalid flag"):
            add_flag("* * * * *", "unknown_flag", path=flag_file)

    def test_all_valid_flags_accepted(self, flag_file):
        for i, f in enumerate(sorted(VALID_FLAGS)):
            expr = f"* * * * {i}"
            entry = add_flag(expr, f, path=flag_file)
            assert entry.flag == f


class TestRemoveFlag:
    def test_remove_existing_returns_true(self, flag_file):
        add_flag("* * * * *", "active", path=flag_file)
        assert remove_flag("* * * * *", path=flag_file) is True

    def test_remove_missing_returns_false(self, flag_file):
        assert remove_flag("* * * * *", path=flag_file) is False

    def test_remove_reduces_count(self, flag_file):
        add_flag("* * * * *", "active", path=flag_file)
        add_flag("0 0 * * *", "disabled", path=flag_file)
        remove_flag("* * * * *", path=flag_file)
        assert len(list_flags(path=flag_file)) == 1


class TestGetFlag:
    def test_get_existing_returns_entry(self, flag_file):
        add_flag("* * * * *", "active", path=flag_file)
        entry = get_flag("* * * * *", path=flag_file)
        assert entry is not None
        assert entry.flag == "active"

    def test_get_missing_returns_none(self, flag_file):
        entry = get_flag("* * * * *", path=flag_file)
        assert entry is None

    def test_get_returns_correct_entry(self, flag_file):
        add_flag("* * * * *", "active", path=flag_file)
        add_flag("0 0 * * *", "disabled", path=flag_file)
        entry = get_flag("0 0 * * *", path=flag_file)
        assert entry is not None
        assert entry.flag == "disabled"
        assert entry.expression == "0 0 * * *"
