"""Tests for crontab_gen.cmd_history CLI sub-command."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_gen.cmd_history import add_history_subparser, cmd_history
from crontab_gen.history import add_entry


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def _make_args(history_cmd: str = "list", limit: int = 10) -> argparse.Namespace:
    return argparse.Namespace(history_cmd=history_cmd, limit=limit)


class TestAddHistorySubparser:
    def test_registers_history_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_history_subparser(sub)
        args = parser.parse_args(["history", "list", "-n", "5"])
        assert args.limit == 5

    def test_clear_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_history_subparser(sub)
        args = parser.parse_args(["history", "clear"])
        assert args.history_cmd == "clear"


class TestCmdHistoryList:
    def test_empty_history_prints_message(self, hist_file, capsys):
        with patch("crontab_gen.cmd_history.get_history", return_value=[]):
            result = cmd_history(_make_args())
        assert result == 0
        captured = capsys.readouterr()
        assert "No history" in captured.out

    def test_lists_entries(self, hist_file, capsys):
        add_entry("0 * * * *", "hourly", path=hist_file)
        add_entry("* * * * *", "every minute", path=hist_file)
        with patch(
            "crontab_gen.cmd_history.get_history",
            side_effect=lambda **kw: __import__(
                "crontab_gen.history", fromlist=["get_history"]
            ).get_history(path=hist_file, **kw),
        ):
            result = cmd_history(_make_args(limit=10))
        assert result == 0

    def test_returns_zero_on_success(self, capsys):
        with patch("crontab_gen.cmd_history.get_history", return_value=[]):
            assert cmd_history(_make_args()) == 0


class TestCmdHistoryClear:
    def test_clear_prints_count(self, hist_file, capsys):
        with patch("crontab_gen.cmd_history.clear_history", return_value=3) as mock_clear:
            result = cmd_history(_make_args(history_cmd="clear"))
        assert result == 0
        captured = capsys.readouterr()
        assert "3" in captured.out
        mock_clear.assert_called_once()
