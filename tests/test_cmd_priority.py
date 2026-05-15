"""Tests for crontab_gen.cmd_priority."""
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from crontab_gen.cmd_priority import add_priority_subparser, cmd_priority
from crontab_gen.priority import add_priority, list_priorities


@pytest.fixture
def pri_file(tmp_path) -> Path:
    return tmp_path / "priorities.json"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "priority_cmd": "list",
        "expression": None,
        "level": None,
        "label": None,
        "file": None,
        "func": cmd_priority,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddPrioritySubparser:
    def test_registers_priority_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_priority_subparser(sub)
        args = parser.parse_args(["priority", "list"])
        assert args.cmd == "priority"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_priority_subparser(sub)
        args = parser.parse_args(["priority", "add", "* * * * *", "high"])
        assert args.priority_cmd == "add"
        assert args.expression == "* * * * *"
        assert args.level == "high"

    def test_remove_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_priority_subparser(sub)
        args = parser.parse_args(["priority", "remove", "* * * * *"])
        assert args.priority_cmd == "remove"

    def test_list_level_filter(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_priority_subparser(sub)
        args = parser.parse_args(["priority", "list", "--level", "critical"])
        assert args.level == "critical"


class TestCmdPriority:
    def test_add_valid_expression(self, pri_file, capsys):
        args = _make_args(priority_cmd="add", expression="* * * * *",
                          level="low", file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "low" in out

    def test_add_invalid_expression_prints_error(self, pri_file, capsys):
        args = _make_args(priority_cmd="add", expression="not-valid",
                          level="low", file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "Error" in out

    def test_list_empty(self, pri_file, capsys):
        args = _make_args(priority_cmd="list", file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "No prioritised" in out

    def test_list_shows_entries(self, pri_file, capsys):
        add_priority("0 * * * *", "high", path=pri_file)
        args = _make_args(priority_cmd="list", file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "high" in out
        assert "0 * * * *" in out

    def test_remove_existing(self, pri_file, capsys):
        add_priority("0 * * * *", "medium", path=pri_file)
        args = _make_args(priority_cmd="remove", expression="0 * * * *",
                          file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_missing(self, pri_file, capsys):
        args = _make_args(priority_cmd="remove", expression="0 * * * *",
                          file=str(pri_file))
        cmd_priority(args)
        out = capsys.readouterr().out
        assert "No priority tag" in out
