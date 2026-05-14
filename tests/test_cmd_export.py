"""Tests for crontab_gen.cmd_export."""
from __future__ import annotations

import argparse
from types import SimpleNamespace
from typing import List, Optional

import pytest

from crontab_gen.cmd_export import add_export_subparser, cmd_export


def _make_args(
    expressions: List[str],
    fmt: str = "json",
    labels: Optional[List[str]] = None,
) -> SimpleNamespace:
    return SimpleNamespace(expressions=expressions, fmt=fmt, labels=labels)


class TestAddExportSubparser:
    def test_registers_export_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_export_subparser(sub)
        args = parser.parse_args(["export", "* * * * *"])
        assert hasattr(args, "func")

    def test_default_format_is_json(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_export_subparser(sub)
        args = parser.parse_args(["export", "* * * * *"])
        assert args.fmt == "json"

    def test_format_flag_sets_shell(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_export_subparser(sub)
        args = parser.parse_args(["export", "* * * * *", "--format", "shell"])
        assert args.fmt == "shell"


class TestCmdExport:
    def test_invalid_expression_returns_1(self, capsys):
        args = _make_args(["not-valid"])
        rc = cmd_export(args)
        assert rc == 1

    def test_valid_expression_returns_0(self, capsys):
        args = _make_args(["* * * * *"])
        rc = cmd_export(args)
        assert rc == 0

    def test_json_output_printed(self, capsys):
        args = _make_args(["0 0 * * *"], fmt="json")
        cmd_export(args)
        out = capsys.readouterr().out
        assert "0 0 * * *" in out

    def test_shell_output_printed(self, capsys):
        args = _make_args(["0 0 * * *"], fmt="shell")
        cmd_export(args)
        out = capsys.readouterr().out
        assert "0 0 * * *" in out
        assert "/path/to/command" in out

    def test_markdown_output_printed(self, capsys):
        args = _make_args(["0 0 * * *"], fmt="markdown")
        cmd_export(args)
        out = capsys.readouterr().out
        assert "| Expression |" in out

    def test_mismatched_labels_returns_1(self, capsys):
        args = _make_args(["* * * * *", "0 0 * * *"], labels=["only-one"])
        rc = cmd_export(args)
        assert rc == 1

    def test_matched_labels_returns_0(self, capsys):
        args = _make_args(["* * * * *"], labels=["heartbeat"])
        rc = cmd_export(args)
        assert rc == 0
