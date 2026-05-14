"""Tests for crontab_gen.cmd_suggest."""

from __future__ import annotations

import argparse
import pytest

from crontab_gen.cmd_suggest import add_suggest_subparser, cmd_suggest, _format_suggestions
from crontab_gen.suggest import Suggestion


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"query": "", "limit": 5, "no_header": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddSuggestSubparser:
    def test_registers_suggest_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest"])
        assert hasattr(args, "func")

    def test_query_is_optional(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest"])
        assert args.query == ""

    def test_query_is_captured(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest", "daily"])
        assert args.query == "daily"

    def test_limit_default(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest"])
        assert args.limit == 5

    def test_limit_flag(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest", "--limit", "3"])
        assert args.limit == 3

    def test_no_header_default_false(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest"])
        assert args.no_header is False

    def test_no_header_flag(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_suggest_subparser(sub)
        args = parser.parse_args(["suggest", "--no-header"])
        assert args.no_header is True


class TestFormatSuggestions:
    def test_empty_list_returns_no_suggestions_message(self):
        result = _format_suggestions([], no_header=False)
        assert "No suggestions found" in result

    def test_header_present_by_default(self):
        suggestions = [Suggestion("0 * * * *", "Every hour", [])]
        result = _format_suggestions(suggestions, no_header=False)
        assert "Expression" in result

    def test_no_header_suppresses_header(self):
        suggestions = [Suggestion("0 * * * *", "Every hour", [])]
        result = _format_suggestions(suggestions, no_header=True)
        assert "Expression" not in result

    def test_expression_in_output(self):
        suggestions = [Suggestion("0 * * * *", "Every hour", [])]
        result = _format_suggestions(suggestions, no_header=False)
        assert "0 * * * *" in result

    def test_description_in_output(self):
        suggestions = [Suggestion("0 * * * *", "Every hour", [])]
        result = _format_suggestions(suggestions, no_header=False)
        assert "Every hour" in result


class TestCmdSuggest:
    def test_returns_zero(self, capsys):
        args = _make_args(query="daily")
        result = cmd_suggest(args)
        assert result == 0

    def test_prints_output(self, capsys):
        args = _make_args(query="hourly")
        cmd_suggest(args)
        captured = capsys.readouterr()
        assert len(captured.out.strip()) > 0
