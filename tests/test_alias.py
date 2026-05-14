"""Tests for crontab_gen.alias module."""
import json
import os
import pytest

from crontab_gen.alias import (
    AliasEntry,
    add_alias,
    get_alias,
    list_aliases,
    remove_alias,
)


@pytest.fixture()
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


class TestAliasEntry:
    def test_to_dict_roundtrip(self):
        entry = AliasEntry(name="daily", expression="0 0 * * *", description="Every midnight")
        restored = AliasEntry.from_dict(entry.to_dict())
        assert restored.name == entry.name
        assert restored.expression == entry.expression
        assert restored.description == entry.description

    def test_defaults(self):
        entry = AliasEntry(name="x", expression="* * * * *")
        assert entry.description == ""


class TestAddAlias:
    def test_add_creates_entry(self, alias_file):
        entry = add_alias("nightly", "0 2 * * *", path=alias_file)
        assert entry.name == "nightly"
        assert entry.expression == "0 2 * * *"

    def test_add_persists_to_file(self, alias_file):
        add_alias("nightly", "0 2 * * *", path=alias_file)
        with open(alias_file) as fh:
            data = json.load(fh)
        assert any(e["name"] == "nightly" for e in data)

    def test_add_overwrites_existing_name(self, alias_file):
        add_alias("x", "0 1 * * *", path=alias_file)
        add_alias("x", "0 2 * * *", path=alias_file)
        entries = list_aliases(path=alias_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 2 * * *"

    def test_add_case_insensitive_overwrite(self, alias_file):
        add_alias("Daily", "0 0 * * *", path=alias_file)
        add_alias("daily", "0 1 * * *", path=alias_file)
        entries = list_aliases(path=alias_file)
        assert len(entries) == 1


class TestGetAlias:
    def test_returns_entry(self, alias_file):
        add_alias("weekly", "0 0 * * 0", path=alias_file)
        entry = get_alias("weekly", path=alias_file)
        assert entry is not None
        assert entry.expression == "0 0 * * 0"

    def test_returns_none_for_unknown(self, alias_file):
        assert get_alias("ghost", path=alias_file) is None

    def test_case_insensitive_lookup(self, alias_file):
        add_alias("Weekly", "0 0 * * 0", path=alias_file)
        assert get_alias("weekly", path=alias_file) is not None


class TestRemoveAlias:
    def test_remove_existing_returns_true(self, alias_file):
        add_alias("tmp", "* * * * *", path=alias_file)
        assert remove_alias("tmp", path=alias_file) is True

    def test_remove_nonexistent_returns_false(self, alias_file):
        assert remove_alias("ghost", path=alias_file) is False

    def test_remove_deletes_entry(self, alias_file):
        add_alias("a", "* * * * *", path=alias_file)
        add_alias("b", "0 0 * * *", path=alias_file)
        remove_alias("a", path=alias_file)
        entries = list_aliases(path=alias_file)
        assert len(entries) == 1
        assert entries[0].name == "b"


class TestListAliases:
    def test_empty_when_no_file(self, alias_file):
        assert list_aliases(path=alias_file) == []

    def test_returns_all_entries(self, alias_file):
        add_alias("a", "* * * * *", path=alias_file)
        add_alias("b", "0 0 * * *", path=alias_file)
        assert len(list_aliases(path=alias_file)) == 2
