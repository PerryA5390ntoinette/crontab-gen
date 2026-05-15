"""Tests for crontab_gen.group module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_gen.group import (
    GroupEntry,
    add_group,
    get_group,
    list_groups,
    remove_group,
)


@pytest.fixture()
def grp_file(tmp_path: Path) -> Path:
    return tmp_path / "groups.json"


class TestGroupEntry:
    def test_to_dict_roundtrip(self):
        e = GroupEntry(name="nightly", expressions=["0 2 * * *", "30 3 * * *"])
        d = e.to_dict()
        restored = GroupEntry.from_dict(d)
        assert restored.name == e.name
        assert restored.expressions == e.expressions

    def test_description_excluded_when_none(self):
        e = GroupEntry(name="g", expressions=["* * * * *"])
        assert "description" not in e.to_dict()

    def test_description_included_when_set(self):
        e = GroupEntry(name="g", expressions=["* * * * *"], description="My group")
        assert e.to_dict()["description"] == "My group"

    def test_created_at_is_set(self):
        e = GroupEntry(name="g", expressions=["* * * * *"])
        assert e.created_at is not None
        assert "T" in e.created_at


class TestAddGroup:
    def test_adds_entry(self, grp_file):
        add_group("daily", ["0 0 * * *"], path=grp_file)
        entries = list_groups(path=grp_file)
        assert len(entries) == 1
        assert entries[0].name == "daily"

    def test_returns_entry(self, grp_file):
        e = add_group("weekly", ["0 0 * * 0"], path=grp_file)
        assert isinstance(e, GroupEntry)
        assert e.name == "weekly"

    def test_multiple_expressions_stored(self, grp_file):
        add_group("multi", ["* * * * *", "0 12 * * *"], path=grp_file)
        e = get_group("multi", path=grp_file)
        assert e is not None
        assert len(e.expressions) == 2

    def test_description_stored(self, grp_file):
        add_group("g", ["* * * * *"], description="desc here", path=grp_file)
        e = get_group("g", path=grp_file)
        assert e is not None
        assert e.description == "desc here"


class TestRemoveGroup:
    def test_remove_existing(self, grp_file):
        add_group("to_remove", ["* * * * *"], path=grp_file)
        result = remove_group("to_remove", path=grp_file)
        assert result is True
        assert list_groups(path=grp_file) == []

    def test_remove_nonexistent_returns_false(self, grp_file):
        result = remove_group("ghost", path=grp_file)
        assert result is False


class TestGetGroup:
    def test_get_existing(self, grp_file):
        add_group("find_me", ["5 4 * * *"], path=grp_file)
        e = get_group("find_me", path=grp_file)
        assert e is not None
        assert e.name == "find_me"

    def test_get_missing_returns_none(self, grp_file):
        assert get_group("missing", path=grp_file) is None

    def test_persisted_to_json(self, grp_file):
        add_group("persist", ["0 6 * * 1"], path=grp_file)
        raw = json.loads(grp_file.read_text())
        assert any(r["name"] == "persist" for r in raw)
