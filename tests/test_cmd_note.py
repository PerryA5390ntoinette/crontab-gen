"""Tests for crontab_gen.cmd_note module."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from crontab_gen.cmd_note import add_note_subparser, cmd_note


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"note_cmd": "list", "expression": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddNoteSubparser:
    def test_registers_note_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_note_subparser(sub)
        args = parser.parse_args(["note", "list"])
        assert args.cmd == "note"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_note_subparser(sub)
        args = parser.parse_args(["note", "add", "* * * * *", "my note"])
        assert args.note_cmd == "add"
        assert args.expression == "* * * * *"
        assert args.text == "my note"

    def test_remove_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_note_subparser(sub)
        args = parser.parse_args(["note", "remove", "* * * * *", "0"])
        assert args.note_cmd == "remove"
        assert args.index == 0

    def test_update_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_note_subparser(sub)
        args = parser.parse_args(["note", "update", "* * * * *", "1", "updated text"])
        assert args.note_cmd == "update"
        assert args.index == 1
        assert args.text == "updated text"


class TestCmdNote:
    def test_add_prints_confirmation(self, tmp_path, capsys):
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", tmp_path / "notes.json"):
            args = _make_args(note_cmd="add", expression="* * * * *", text="test note")
            cmd_note(args)
        out = capsys.readouterr().out
        assert "Note added" in out
        assert "test note" in out

    def test_list_empty_prints_message(self, tmp_path, capsys):
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", tmp_path / "notes.json"):
            args = _make_args(note_cmd="list", expression=None)
            cmd_note(args)
        out = capsys.readouterr().out
        assert "No notes" in out

    def test_list_shows_entries(self, tmp_path, capsys):
        p = tmp_path / "notes.json"
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", p):
            add_args = _make_args(note_cmd="add", expression="0 * * * *", text="hourly job")
            cmd_note(add_args)
            list_args = _make_args(note_cmd="list", expression=None)
            cmd_note(list_args)
        out = capsys.readouterr().out
        assert "hourly job" in out

    def test_remove_valid_prints_confirmation(self, tmp_path, capsys):
        p = tmp_path / "notes.json"
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", p):
            cmd_note(_make_args(note_cmd="add", expression="* * * * *", text="removable"))
            capsys.readouterr()
            cmd_note(_make_args(note_cmd="remove", expression="* * * * *", index=0))
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_invalid_prints_not_found(self, tmp_path, capsys):
        p = tmp_path / "notes.json"
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", p):
            cmd_note(_make_args(note_cmd="remove", expression="* * * * *", index=0))
        out = capsys.readouterr().out
        assert "No note" in out

    def test_update_valid_prints_confirmation(self, tmp_path, capsys):
        p = tmp_path / "notes.json"
        with patch("crontab_gen.cmd_note._DEFAULT_PATH", p):
            cmd_note(_make_args(note_cmd="add", expression="* * * * *", text="old"))
            capsys.readouterr()
            cmd_note(_make_args(note_cmd="update", expression="* * * * *", index=0, text="new"))
        out = capsys.readouterr().out
        assert "updated" in out
        assert "new" in out
