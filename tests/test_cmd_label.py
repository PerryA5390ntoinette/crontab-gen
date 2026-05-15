"""Tests for crontab_gen.cmd_label module."""
import argparse
import sys
import pytest

from crontab_gen.cmd_label import add_label_subparser, cmd_label
from crontab_gen.label import add_label, list_labels


def _make_args(**kwargs):
    base = {"label_cmd": None, "expression": None, "label": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


class TestAddLabelSubparser:
    def test_registers_label_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_label_subparser(sub)
        args = parser.parse_args(["label", "list"])
        assert args.cmd == "label"

    def test_add_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_label_subparser(sub)
        args = parser.parse_args(["label", "add", "* * * * *", "every minute"])
        assert args.label_cmd == "add"
        assert args.expression == "* * * * *"
        assert args.label == "every minute"

    def test_remove_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_label_subparser(sub)
        args = parser.parse_args(["label", "remove", "* * * * *"])
        assert args.label_cmd == "remove"
        assert args.expression == "* * * * *"

    def test_show_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_label_subparser(sub)
        args = parser.parse_args(["label", "show", "0 * * * *"])
        assert args.label_cmd == "show"


class TestCmdLabel:
    def test_add_valid_expression(self, tmp_path, capsys, monkeypatch):
        path = str(tmp_path / "labels.json")
        monkeypatch.setattr("crontab_gen.cmd_label.add_label",
                            lambda expr, lbl: __import__(
                                "crontab_gen.label", fromlist=["add_label"]
                            ).add_label(expr, lbl, path=path))
        args = _make_args(label_cmd="add", expression="* * * * *", label="every minute")
        cmd_label(args)
        captured = capsys.readouterr()
        assert "every minute" in captured.out

    def test_add_invalid_expression_exits(self, capsys):
        args = _make_args(label_cmd="add", expression="bad expr", label="test")
        with pytest.raises(SystemExit) as exc:
            cmd_label(args)
        assert exc.value.code == 1

    def test_list_empty(self, tmp_path, capsys, monkeypatch):
        path = str(tmp_path / "labels.json")
        monkeypatch.setattr("crontab_gen.cmd_label.list_labels",
                            lambda: [])
        args = _make_args(label_cmd="list")
        cmd_label(args)
        captured = capsys.readouterr()
        assert "No labels" in captured.out

    def test_no_subcommand_exits(self, capsys):
        args = _make_args(label_cmd=None)
        with pytest.raises(SystemExit) as exc:
            cmd_label(args)
        assert exc.value.code == 1

    def test_remove_nonexistent_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr("crontab_gen.cmd_label.remove_label",
                            lambda expr: False)
        args = _make_args(label_cmd="remove", expression="* * * * *")
        with pytest.raises(SystemExit) as exc:
            cmd_label(args)
        assert exc.value.code == 1
