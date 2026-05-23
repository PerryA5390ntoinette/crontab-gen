"""Tests for crontab_gen.cmd_density."""

from __future__ import annotations

import argparse
from unittest.mock import patch, MagicMock

import pytest

from crontab_gen.cmd_density import add_density_subparser, cmd_density
from crontab_gen.density import DensityResult


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"expression": "0 * * * *", "hours": 24}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------

class TestAddDensitySubparser:
    def _parser(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers()
        add_density_subparser(sub)
        return p

    def test_registers_density_command(self):
        p = self._parser()
        ns = p.parse_args(["density", "* * * * *"])
        assert ns.func is cmd_density

    def test_default_hours_is_24(self):
        p = self._parser()
        ns = p.parse_args(["density", "* * * * *"])
        assert ns.hours == 24

    def test_hours_flag_sets_value(self):
        p = self._parser()
        ns = p.parse_args(["density", "* * * * *", "--hours", "48"])
        assert ns.hours == 48

    def test_expression_is_captured(self):
        p = self._parser()
        ns = p.parse_args(["density", "0 9 * * *"])
        assert ns.expression == "0 9 * * *"


# ---------------------------------------------------------------------------
# cmd_density behaviour
# ---------------------------------------------------------------------------

class TestCmdDensity:
    def _fake_result(self, expr="0 * * * *") -> DensityResult:
        return DensityResult(
            expression=expr,
            window_hours=24,
            fire_count=24,
            label="medium",
        )

    def test_prints_result_on_success(self, capsys):
        with patch("crontab_gen.cmd_density.analyse_density", return_value=self._fake_result()):
            cmd_density(_make_args())
        out = capsys.readouterr().out
        assert "medium" in out

    def test_prints_error_on_invalid_expression(self, capsys):
        with patch(
            "crontab_gen.cmd_density.analyse_density",
            side_effect=ValueError("Invalid cron expression: 'bad'"),
        ):
            cmd_density(_make_args(expression="bad"))
        out = capsys.readouterr().out
        assert "Error" in out

    def test_passes_hours_to_analyse(self):
        with patch("crontab_gen.cmd_density.analyse_density", return_value=self._fake_result()) as mock:
            cmd_density(_make_args(hours=48))
        mock.assert_called_once_with("0 * * * *", window_hours=48)
