"""Tests for crontab_gen.bookmark and cmd_bookmark."""
from __future__ import annotations

import argparse
import json
import os
import pytest

from crontab_gen.bookmark import (
    BookmarkEntry,
    add_bookmark,
    find_bookmark,
    list_bookmarks,
    remove_bookmark,
)
from crontab_gen.cmd_bookmark import add_bookmark_subparser, cmd_bookmark


@pytest.fixture()
def bm_file(tmp_path):
    return str(tmp_path / "bookmarks.json")


class TestBookmarkEntry:
    def test_to_dict_roundtrip(self):
        entry = BookmarkEntry(expression="0 9 * * 1", label="weekly")
        restored = BookmarkEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.label == entry.label
        assert restored.created_at == entry.created_at

    def test_created_at_is_set(self):
        entry = BookmarkEntry(expression="* * * * *", label="every-min")
        assert entry.created_at != ""


class TestAddBookmark:
    def test_add_creates_file(self, bm_file):
        add_bookmark("* * * * *", "every-min", path=bm_file)
        assert os.path.exists(bm_file)

    def test_add_returns_entry(self, bm_file):
        entry = add_bookmark("0 0 * * *", "midnight", path=bm_file)
        assert entry.expression == "0 0 * * *"
        assert entry.label == "midnight"

    def test_multiple_bookmarks_persisted(self, bm_file):
        add_bookmark("* * * * *", "a", path=bm_file)
        add_bookmark("0 0 * * *", "b", path=bm_file)
        entries = list_bookmarks(path=bm_file)
        assert len(entries) == 2


class TestRemoveBookmark:
    def test_remove_existing_returns_true(self, bm_file):
        add_bookmark("* * * * *", "to-remove", path=bm_file)
        result = remove_bookmark("to-remove", path=bm_file)
        assert result is True

    def test_remove_nonexistent_returns_false(self, bm_file):
        result = remove_bookmark("ghost", path=bm_file)
        assert result is False

    def test_entry_gone_after_remove(self, bm_file):
        add_bookmark("* * * * *", "gone", path=bm_file)
        remove_bookmark("gone", path=bm_file)
        assert find_bookmark("gone", path=bm_file) is None


class TestFindBookmark:
    def test_find_existing(self, bm_file):
        add_bookmark("0 12 * * *", "noon", path=bm_file)
        entry = find_bookmark("noon", path=bm_file)
        assert entry is not None
        assert entry.expression == "0 12 * * *"

    def test_find_missing_returns_none(self, bm_file):
        assert find_bookmark("missing", path=bm_file) is None


class TestAddBookmarkSubparser:
    def test_registers_bookmark_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_bookmark_subparser(sub)
        args = parser.parse_args(["bookmark", "list"])
        assert args.command == "bookmark"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_bookmark_subparser(sub)
        args = parser.parse_args(["bookmark", "add", "* * * * *", "every-min"])
        assert args.bookmark_cmd == "add"
        assert args.expression == "* * * * *"
        assert args.label == "every-min"

    def test_remove_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_bookmark_subparser(sub)
        args = parser.parse_args(["bookmark", "remove", "noon"])
        assert args.bookmark_cmd == "remove"
        assert args.label == "noon"
