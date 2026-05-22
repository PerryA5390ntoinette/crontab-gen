"""Tests for crontab_gen.cmd_forecast."""
from __future__ import annotations

import argparse
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

from crontab_gen.cmd_forecast import add_forecast_subparser, cmd_forecast


def _make_args(**kwargs):
    defaults = {
        "expression": "* * * * *",
        "hours": 24,
        "count_only": False,
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    ns.func = cmd_forecast
    return ns


class TestAddForecastSubparser:
    def _parser(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers()
        add_forecast_subparser(sub)
        return p

    def test_registers_forecast_command(self):
        p = self._parser()
        args = p.parse_args(["forecast", "* * * * *"])
        assert args.func is cmd_forecast

    def test_default_hours_is_24(self):
        p = self._parser()
        args = p.parse_args(["forecast", "* * * * *"])
        assert args.hours == 24

    def test_hours_flag_sets_value(self):
        p = self._parser()
        args = p.parse_args(["forecast", "* * * * *", "--hours", "48"])
        assert args.hours == 48

    def test_count_only_default_false(self):
        p = self._parser()
        args = p.parse_args(["forecast", "* * * * *"])
        assert args.count_only is False

    def test_count_only_flag_sets_true(self):
        p = self._parser()
        args = p.parse_args(["forecast", "* * * * *", "--count-only"])
        assert args.count_only is True

    def test_expression_is_captured(self):
        p = self._parser()
        args = p.parse_args(["forecast", "0 9 * * 1"])
        assert args.expression == "0 9 * * 1"


class TestCmdForecast:
    def test_invalid_expression_exits(self):
        args = _make_args(expression="bad expr")
        with pytest.raises(SystemExit) as exc_info:
            cmd_forecast(args)
        assert exc_info.value.code == 1

    def test_prints_result(self, capsys):
        args = _make_args(expression="* * * * *", hours=1)
        cmd_forecast(args)
        captured = capsys.readouterr()
        assert "* * * * *" in captured.out

    def test_count_only_prints_integer(self, capsys):
        args = _make_args(expression="* * * * *", hours=1, count_only=True)
        cmd_forecast(args)
        captured = capsys.readouterr()
        assert captured.out.strip().isdigit()

    def test_error_goes_to_stderr(self, capsys):
        args = _make_args(expression="not valid")
        with pytest.raises(SystemExit):
            cmd_forecast(args)
        captured = capsys.readouterr()
        assert "Error" in captured.err
