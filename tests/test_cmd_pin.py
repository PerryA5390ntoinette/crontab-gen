"""Tests for crontab_gen/cmd_pin.py"""
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from crontab_gen.cmd_pin import add_pin_subparser, cmd_pin
from crontab_gen import pin as pin_mod


@pytest.fixture
def pin_file(tmp_path):
    return tmp_path / "pins.json"


def _make_args(**kwargs):
    defaults = {"pin_cmd": "list", "file": None, "func": cmd_pin}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddPinSubparser:
    def test_registers_pin_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_pin_subparser(sub)
        args = parser.parse_args(["pin", "list"])
        assert args.cmd == "pin"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_pin_subparser(sub)
        args = parser.parse_args(["pin", "add", "* * * * *"])
        assert args.pin_cmd == "add"
        assert args.expression == "* * * * *"

    def test_add_with_label(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_pin_subparser(sub)
        args = parser.parse_args(["pin", "add", "* * * * *", "--label", "every minute"])
        assert args.label == "every minute"

    def test_remove_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_pin_subparser(sub)
        args = parser.parse_args(["pin", "remove", "* * * * *"])
        assert args.pin_cmd == "remove"

    def test_clear_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_pin_subparser(sub)
        args = parser.parse_args(["pin", "clear"])
        assert args.pin_cmd == "clear"


class TestCmdPin:
    def test_add_valid_expression(self, pin_file, capsys):
        args = _make_args(pin_cmd="add", expression="* * * * *", label=None, file=str(pin_file))
        cmd_pin(args)
        captured = capsys.readouterr()
        assert "Pinned" in captured.out

    def test_add_invalid_expression_exits(self, pin_file):
        args = _make_args(pin_cmd="add", expression="invalid", label=None, file=str(pin_file))
        with pytest.raises(SystemExit) as exc:
            cmd_pin(args)
        assert exc.value.code == 1

    def test_list_empty(self, pin_file, capsys):
        args = _make_args(pin_cmd="list", file=str(pin_file))
        cmd_pin(args)
        captured = capsys.readouterr()
        assert "No pinned" in captured.out

    def test_list_shows_expression(self, pin_file, capsys):
        pin_mod.add_pin("0 9 * * 1", path=pin_file)
        args = _make_args(pin_cmd="list", file=str(pin_file))
        cmd_pin(args)
        captured = capsys.readouterr()
        assert "0 9 * * 1" in captured.out

    def test_remove_existing(self, pin_file, capsys):
        pin_mod.add_pin("* * * * *", path=pin_file)
        args = _make_args(pin_cmd="remove", expression="* * * * *", file=str(pin_file))
        cmd_pin(args)
        captured = capsys.readouterr()
        assert "Unpinned" in captured.out

    def test_remove_nonexistent_exits(self, pin_file):
        args = _make_args(pin_cmd="remove", expression="* * * * *", file=str(pin_file))
        with pytest.raises(SystemExit) as exc:
            cmd_pin(args)
        assert exc.value.code == 1

    def test_clear_prints_count(self, pin_file, capsys):
        pin_mod.add_pin("* * * * *", path=pin_file)
        pin_mod.add_pin("0 0 * * *", path=pin_file)
        args = _make_args(pin_cmd="clear", file=str(pin_file))
        cmd_pin(args)
        captured = capsys.readouterr()
        assert "2" in captured.out
