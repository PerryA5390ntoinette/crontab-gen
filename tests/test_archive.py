"""Tests for crontab_gen.archive module and cmd_archive."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from crontab_gen.archive import (
    ArchiveEntry,
    archive_expression,
    clear_archive,
    list_archive,
    remove_from_archive,
)
from crontab_gen.cmd_archive import add_archive_subparser, cmd_archive


@pytest.fixture
def arch_file(tmp_path: Path) -> Path:
    return tmp_path / "archive.json"


class TestArchiveEntry:
    def test_to_dict_roundtrip(self):
        e = ArchiveEntry(expression="* * * * *", label="every minute", source="bookmark")
        d = e.to_dict()
        restored = ArchiveEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.label == e.label
        assert restored.source == e.source
        assert restored.archived_at == e.archived_at

    def test_label_excluded_when_none(self):
        e = ArchiveEntry(expression="0 * * * *")
        assert "label" not in e.to_dict()

    def test_source_excluded_when_none(self):
        e = ArchiveEntry(expression="0 * * * *")
        assert "source" not in e.to_dict()

    def test_archived_at_is_set(self):
        e = ArchiveEntry(expression="0 0 * * *")
        assert e.archived_at is not None
        assert "T" in e.archived_at  # ISO format


class TestArchiveExpression:
    def test_add_creates_entry(self, arch_file):
        entry = archive_expression("5 4 * * *", path=arch_file)
        assert entry.expression == "5 4 * * *"

    def test_add_persists(self, arch_file):
        archive_expression("0 12 * * 1", label="monday noon", path=arch_file)
        entries = list_archive(path=arch_file)
        assert len(entries) == 1
        assert entries[0].label == "monday noon"

    def test_multiple_entries(self, arch_file):
        archive_expression("* * * * *", path=arch_file)
        archive_expression("0 0 * * *", path=arch_file)
        assert len(list_archive(path=arch_file)) == 2

    def test_empty_archive_returns_empty_list(self, arch_file):
        assert list_archive(path=arch_file) == []


class TestRemoveFromArchive:
    def test_remove_existing(self, arch_file):
        archive_expression("* * * * *", path=arch_file)
        removed = remove_from_archive("* * * * *", path=arch_file)
        assert removed is True
        assert list_archive(path=arch_file) == []

    def test_remove_nonexistent_returns_false(self, arch_file):
        removed = remove_from_archive("0 0 * * *", path=arch_file)
        assert removed is False


class TestClearArchive:
    def test_clear_returns_count(self, arch_file):
        archive_expression("* * * * *", path=arch_file)
        archive_expression("0 0 * * *", path=arch_file)
        count = clear_archive(path=arch_file)
        assert count == 2

    def test_clear_empties_store(self, arch_file):
        archive_expression("* * * * *", path=arch_file)
        clear_archive(path=arch_file)
        assert list_archive(path=arch_file) == []


class TestAddArchiveSubparser:
    def test_registers_archive_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_archive_subparser(sub)
        args = parser.parse_args(["archive", "list"])
        assert args.cmd == "archive"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_archive_subparser(sub)
        args = parser.parse_args(["archive", "add", "0 9 * * 1", "--label", "weekly"])
        assert args.expression == "0 9 * * 1"
        assert args.label == "weekly"

    def test_clear_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_archive_subparser(sub)
        args = parser.parse_args(["archive", "clear"])
        assert args.archive_cmd == "clear"
