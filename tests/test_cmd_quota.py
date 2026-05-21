"""Tests for crontab_gen.cmd_quota."""
from __future__ import annotations

import argparse
import sys
from unittest.mock import patch, MagicMock

import pytest

from crontab_gen.cmd_quota import add_quota_subparser, cmd_quota


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        expression="0 * * * *",
        limit=60,
        window_hours=24,
        func=cmd_quota,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddQuotaSubparser:
    def test_registers_quota_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_quota_subparser(sub)
        args = parser.parse_args(["quota", "* * * * *"])
        assert args.func is cmd_quota

    def test_default_limit_is_60(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_quota_subparser(sub)
        args = parser.parse_args(["quota", "* * * * *"])
        assert args.limit == 60

    def test_default_window_is_24(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_quota_subparser(sub)
        args = parser.parse_args(["quota", "* * * * *"])
        assert args.window_hours == 24

    def test_custom_limit_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_quota_subparser(sub)
        args = parser.parse_args(["quota", "* * * * *", "--limit", "10"])
        assert args.limit == 10

    def test_custom_window_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_quota_subparser(sub)
        args = parser.parse_args(["quota", "* * * * *", "--window", "6"])
        assert args.window_hours == 6


class TestCmdQuota:
    def test_prints_result_on_ok(self, capsys):
        args = _make_args(expression="0 * * * *", limit=60, window_hours=24)
        cmd_quota(args)
        out = capsys.readouterr().out
        assert "0 * * * *" in out

    def test_exits_1_on_invalid_expression(self):
        args = _make_args(expression="not valid")
        with pytest.raises(SystemExit) as exc_info:
            cmd_quota(args)
        assert exc_info.value.code == 1

    def test_exits_1_when_quota_exceeded(self):
        args = _make_args(expression="* * * * *", limit=1, window_hours=1)
        with pytest.raises(SystemExit) as exc_info:
            cmd_quota(args)
        assert exc_info.value.code == 1

    def test_no_exit_when_within_quota(self):
        args = _make_args(expression="0 0 * * *", limit=5, window_hours=24)
        # Should not raise
        cmd_quota(args)
