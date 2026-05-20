"""Tests for crontab_gen.status and crontab_gen.cmd_status."""
from __future__ import annotations

import argparse
import json
import types
from pathlib import Path

import pytest

from crontab_gen.status import StatusReport, _safe_load, build_status
from crontab_gen.cmd_status import add_status_subparser, cmd_status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_entries(path: Path, entries: list) -> None:
    path.write_text(json.dumps(entries))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        bookmarks=None,
        favorites=None,
        history=None,
        notes=None,
        snapshots=None,
        tags=None,
        templates=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# StatusReport
# ---------------------------------------------------------------------------

class TestStatusReport:
    def test_default_counts_are_zero(self):
        r = StatusReport()
        assert r.bookmarks == 0
        assert r.favorites == 0
        assert r.history_entries == 0
        assert r.notes == 0
        assert r.snapshots == 0
        assert r.tags == 0
        assert r.templates == 0

    def test_counts_set_correctly(self):
        r = StatusReport(bookmarks=3, favorites=5)
        assert r.bookmarks == 3
        assert r.favorites == 5


# ---------------------------------------------------------------------------
# _safe_load
# ---------------------------------------------------------------------------

class TestSafeLoad:
    def test_returns_list_on_success(self):
        result = _safe_load(lambda: [1, 2, 3])
        assert result == [1, 2, 3]

    def test_returns_empty_list_on_exception(self):
        def boom():
            raise FileNotFoundError("nope")

        result = _safe_load(boom)
        assert result == []

    def test_passes_path_argument(self):
        received = []

        def loader(p):
            received.append(p)
            return ["x"]

        _safe_load(loader, "/some/path")
        assert received == ["/some/path"]


# ---------------------------------------------------------------------------
# build_status
# ---------------------------------------------------------------------------

class TestBuildStatus:
    def test_empty_files_give_zero_counts(self, tmp_path):
        for name in ("bm", "fav", "hist", "note", "snap", "tag", "tpl"):
            (tmp_path / f"{name}.json").write_text("[]")

        report = build_status(
            bookmarks_path=str(tmp_path / "bm.json"),
            favorites_path=str(tmp_path / "fav.json"),
            history_path=str(tmp_path / "hist.json"),
            notes_path=str(tmp_path / "note.json"),
            snapshots_path=str(tmp_path / "snap.json"),
            tags_path=str(tmp_path / "tag.json"),
            templates_path=str(tmp_path / "tpl.json"),
        )
        assert report.bookmarks == 0
        assert report.favorites == 0

    def test_missing_files_return_zero_not_error(self):
        report = build_status(
            bookmarks_path="/nonexistent/bm.json",
        )
        assert report.bookmarks == 0


# ---------------------------------------------------------------------------
# add_status_subparser / cmd_status
# ---------------------------------------------------------------------------

class TestAddStatusSubparser:
    def test_registers_status_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_status_subparser(sub)
        args = parser.parse_args(["status"])
        assert args.func is cmd_status

    def test_bookmarks_flag_captured(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_status_subparser(sub)
        args = parser.parse_args(["status", "--bookmarks", "/tmp/bm.json"])
        assert args.bookmarks == "/tmp/bm.json"

    def test_defaults_are_none(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_status_subparser(sub)
        args = parser.parse_args(["status"])
        assert args.favorites is None
        assert args.history is None


class TestCmdStatus:
    def test_cmd_status_prints_output(self, capsys):
        cmd_status(_make_args())
        out = capsys.readouterr().out
        assert "status" in out.lower()

    def test_cmd_status_shows_bookmarks_label(self, capsys):
        cmd_status(_make_args())
        out = capsys.readouterr().out
        assert "Bookmarks" in out
