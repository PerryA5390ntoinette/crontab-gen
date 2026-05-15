"""Tests for crontab_gen.cmd_group module."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_gen.cmd_group import add_group_subparser, cmd_group
from crontab_gen.group import add_group


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(group_cmd="list", name=None, expressions=None, description=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddGroupSubparser:
    def test_registers_group_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_group_subparser(sub)
        args = parser.parse_args(["group", "list"])
        assert args.cmd == "group"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_group_subparser(sub)
        args = parser.parse_args(["group", "add", "nightly", "0 2 * * *"])
        assert args.group_cmd == "add"
        assert args.name == "nightly"
        assert args.expressions == ["0 2 * * *"]

    def test_show_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_group_subparser(sub)
        args = parser.parse_args(["group", "show", "mygroup"])
        assert args.group_cmd == "show"
        assert args.name == "mygroup"


class TestCmdGroup:
    def test_list_empty(self, tmp_path, capsys):
        grp_file = tmp_path / "groups.json"
        args = _make_args(group_cmd="list")
        with patch("crontab_gen.cmd_group.list_groups", return_value=[]):
            cmd_group(args)
        out = capsys.readouterr().out
        assert "No groups" in out

    def test_add_valid_expression(self, tmp_path, capsys):
        grp_file = tmp_path / "groups.json"
        args = _make_args(group_cmd="add", name="daily", expressions=["0 0 * * *"], description=None)
        with patch("crontab_gen.cmd_group.add_group") as mock_add:
            from crontab_gen.group import GroupEntry
            mock_add.return_value = GroupEntry(name="daily", expressions=["0 0 * * *"])
            cmd_group(args)
        out = capsys.readouterr().out
        assert "daily" in out

    def test_add_invalid_expression_exits(self, capsys):
        args = _make_args(group_cmd="add", name="bad", expressions=["not_valid"], description=None)
        with pytest.raises(SystemExit) as exc:
            cmd_group(args)
        assert exc.value.code == 1

    def test_remove_missing_exits(self, capsys):
        args = _make_args(group_cmd="remove", name="ghost")
        with patch("crontab_gen.cmd_group.remove_group", return_value=False):
            with pytest.raises(SystemExit) as exc:
                cmd_group(args)
        assert exc.value.code == 1

    def test_show_missing_exits(self, capsys):
        args = _make_args(group_cmd="show", name="ghost")
        with patch("crontab_gen.cmd_group.get_group", return_value=None):
            with pytest.raises(SystemExit) as exc:
                cmd_group(args)
        assert exc.value.code == 1
