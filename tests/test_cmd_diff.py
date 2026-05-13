"""Tests for crontab_gen.cmd_diff CLI subcommand."""

import argparse
import pytest

from crontab_gen.cmd_diff import add_diff_subparser, cmd_diff


def _make_args(left: str, right: str, changed_only: bool = False) -> argparse.Namespace:
    return argparse.Namespace(left=left, right=right, changed_only=changed_only)


class TestAddDiffSubparser:
    def test_registers_diff_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_diff_subparser(sub)
        args = parser.parse_args(["diff", "* * * * *", "0 * * * *"])
        assert args.func is cmd_diff

    def test_changed_only_flag_default_false(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_diff_subparser(sub)
        args = parser.parse_args(["diff", "* * * * *", "* * * * *"])
        assert args.changed_only is False

    def test_changed_only_flag_can_be_set(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_diff_subparser(sub)
        args = parser.parse_args(["diff", "* * * * *", "* * * * *", "--changed-only"])
        assert args.changed_only is True


class TestCmdDiff:
    def test_identical_returns_zero(self, capsys):
        args = _make_args("0 9 * * 1", "0 9 * * 1")
        rc = cmd_diff(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "identical" in out.lower()

    def test_different_returns_zero(self, capsys):
        args = _make_args("0 9 * * 1", "0 10 * * 1")
        rc = cmd_diff(args)
        assert rc == 0

    def test_invalid_left_returns_one(self, capsys):
        args = _make_args("99 * * * *", "* * * * *")
        rc = cmd_diff(args)
        assert rc == 1
        err = capsys.readouterr().err
        assert "Error" in err

    def test_output_contains_field_names(self, capsys):
        args = _make_args("0 9 * * *", "30 10 * * *")
        cmd_diff(args)
        out = capsys.readouterr().out
        assert "MINUTE" in out
        assert "HOUR" in out

    def test_changed_only_hides_unchanged_fields(self, capsys):
        args = _make_args("0 9 * * *", "0 10 * * *", changed_only=True)
        cmd_diff(args)
        out = capsys.readouterr().out
        assert "HOUR" in out
        assert "MINUTE" not in out
