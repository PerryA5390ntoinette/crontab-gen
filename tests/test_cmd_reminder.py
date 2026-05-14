"""Tests for crontab_gen.cmd_reminder."""
import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_gen.cmd_reminder import add_reminder_subparser, cmd_reminder


@pytest.fixture
def rem_file(tmp_path) -> Path:
    return tmp_path / "reminders.json"


def _make_args(reminder_cmd, **kwargs):
    ns = argparse.Namespace(reminder_cmd=reminder_cmd, **kwargs)
    return ns


class TestAddReminderSubparser:
    def test_registers_reminder_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_reminder_subparser(sub)
        args = parser.parse_args(["reminder", "list"])
        assert args.cmd == "reminder"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_reminder_subparser(sub)
        args = parser.parse_args(["reminder", "add", "* * * * *", "hello"])
        assert args.reminder_cmd == "add"
        assert args.expression == "* * * * *"
        assert args.message == "hello"

    def test_add_with_label(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_reminder_subparser(sub)
        args = parser.parse_args(["reminder", "add", "0 0 * * *", "nightly", "--label", "ops"])
        assert args.label == "ops"

    def test_clear_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_reminder_subparser(sub)
        args = parser.parse_args(["reminder", "clear"])
        assert args.reminder_cmd == "clear"


class TestCmdReminder:
    def test_add_prints_confirmation(self, rem_file, capsys):
        args = _make_args("add", expression="* * * * *", message="test msg", label=None, file=rem_file)
        cmd_reminder(args)
        out = capsys.readouterr().out
        assert "Reminder added" in out
        assert "* * * * *" in out

    def test_add_with_label_shows_label(self, rem_file, capsys):
        args = _make_args("add", expression="0 9 * * 1", message="standup", label="work", file=rem_file)
        cmd_reminder(args)
        out = capsys.readouterr().out
        assert "[work]" in out

    def test_list_shows_entries(self, rem_file, capsys):
        add_args = _make_args("add", expression="5 4 * * *", message="backup", label=None, file=rem_file)
        cmd_reminder(add_args)
        list_args = _make_args("list", file=rem_file)
        cmd_reminder(list_args)
        out = capsys.readouterr().out
        assert "5 4 * * *" in out
        assert "backup" in out

    def test_list_empty_message(self, rem_file, capsys):
        args = _make_args("list", file=rem_file)
        cmd_reminder(args)
        out = capsys.readouterr().out
        assert "No reminders" in out

    def test_clear_reports_count(self, rem_file, capsys):
        add_args = _make_args("add", expression="* * * * *", message="x", label=None, file=rem_file)
        cmd_reminder(add_args)
        capsys.readouterr()
        clear_args = _make_args("clear", file=rem_file)
        cmd_reminder(clear_args)
        out = capsys.readouterr().out
        assert "1" in out
