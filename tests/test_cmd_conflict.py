"""Tests for crontab_gen.cmd_conflict."""
from __future__ import annotations

import argparse
from unittest.mock import patch, MagicMock

import pytest

from crontab_gen.cmd_conflict import add_conflict_subparser, cmd_conflict


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expressions": ["* * * * *", "*/5 * * * *"],
        "horizon": 60,
        "quiet": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddConflictSubparser:
    def test_registers_conflict_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_conflict_subparser(sub)
        args = parser.parse_args(["conflict", "* * * * *", "*/5 * * * *"])
        assert args.func is cmd_conflict

    def test_default_horizon_is_60(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_conflict_subparser(sub)
        args = parser.parse_args(["conflict", "* * * * *", "0 9 * * *"])
        assert args.horizon == 60

    def test_horizon_flag_sets_value(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_conflict_subparser(sub)
        args = parser.parse_args(["conflict", "* * * * *", "0 9 * * *", "--horizon", "10"])
        assert args.horizon == 10

    def test_quiet_flag_default_false(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_conflict_subparser(sub)
        args = parser.parse_args(["conflict", "* * * * *", "0 9 * * *"])
        assert args.quiet is False

    def test_quiet_flag_can_be_set(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_conflict_subparser(sub)
        args = parser.parse_args(["conflict", "* * * * *", "0 9 * * *", "--quiet"])
        assert args.quiet is True


class TestCmdConflict:
    def test_too_few_expressions_exits(self):
        args = _make_args(expressions=["* * * * *"])
        with pytest.raises(SystemExit) as exc:
            cmd_conflict(args)
        assert exc.value.code == 1

    def test_invalid_expression_exits(self, capsys):
        args = _make_args(expressions=["bad", "* * * * *"])
        with pytest.raises(SystemExit) as exc:
            cmd_conflict(args)
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_no_conflict_prints_message(self, capsys):
        args = _make_args(expressions=["0 6 * * *", "0 7 * * *"], horizon=30)
        cmd_conflict(args)
        captured = capsys.readouterr()
        assert "No conflicts" in captured.out

    def test_conflict_prints_expressions(self, capsys):
        args = _make_args(expressions=["* * * * *", "*/2 * * * *"], horizon=10)
        cmd_conflict(args)
        captured = capsys.readouterr()
        assert "CONFLICT" in captured.out

    def test_quiet_mode_exits_zero_on_no_conflict(self):
        args = _make_args(expressions=["0 6 * * *", "0 7 * * *"], horizon=30, quiet=True)
        with pytest.raises(SystemExit) as exc:
            cmd_conflict(args)
        assert exc.value.code == 0

    def test_quiet_mode_exits_one_on_conflict(self):
        args = _make_args(expressions=["* * * * *", "*/2 * * * *"], horizon=10, quiet=True)
        with pytest.raises(SystemExit) as exc:
            cmd_conflict(args)
        assert exc.value.code == 1
