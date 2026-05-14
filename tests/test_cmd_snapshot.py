"""Tests for crontab_gen.cmd_snapshot subcommand."""
import argparse
import pytest
from unittest.mock import patch

from crontab_gen.cmd_snapshot import add_snapshot_subparser, cmd_snapshot
from crontab_gen.snapshot import add_snapshot


@pytest.fixture
def snap_file(tmp_path):
    return str(tmp_path / "snapshots.json")


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"snapshot_cmd": "list", "file": "/tmp/test_snaps.json"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddSnapshotSubparser:
    def test_registers_snapshot_command(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_snapshot_subparser(sub)
        args = p.parse_args(["snapshot", "list"])
        assert args.cmd == "snapshot"

    def test_save_subcommand_parsed(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_snapshot_subparser(sub)
        args = p.parse_args(["snapshot", "save", "0 * * * *"])
        assert args.snapshot_cmd == "save"
        assert args.expression == "0 * * * *"

    def test_save_with_label(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_snapshot_subparser(sub)
        args = p.parse_args(["snapshot", "save", "0 * * * *", "--label", "hourly"])
        assert args.label == "hourly"

    def test_compare_subcommand_parsed(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_snapshot_subparser(sub)
        args = p.parse_args(["snapshot", "compare", "0", "1"])
        assert args.snapshot_cmd == "compare"
        assert args.index_a == 0
        assert args.index_b == 1


class TestCmdSnapshotSave:
    def test_save_valid_expression_prints_output(self, snap_file, capsys):
        args = _make_args(snapshot_cmd="save", expression="0 12 * * *", label=None, file=snap_file)
        cmd_snapshot(args)
        out = capsys.readouterr().out
        assert "0 12 * * *" in out

    def test_save_invalid_expression_exits(self, snap_file):
        args = _make_args(snapshot_cmd="save", expression="not-valid", label=None, file=snap_file)
        with pytest.raises(SystemExit):
            cmd_snapshot(args)


class TestCmdSnapshotList:
    def test_list_empty_prints_message(self, snap_file, capsys):
        args = _make_args(snapshot_cmd="list", file=snap_file)
        cmd_snapshot(args)
        out = capsys.readouterr().out
        assert "No snapshots" in out

    def test_list_shows_entries(self, snap_file, capsys):
        add_snapshot("* * * * *", path=snap_file)
        args = _make_args(snapshot_cmd="list", file=snap_file)
        cmd_snapshot(args)
        out = capsys.readouterr().out
        assert "* * * * *" in out


class TestCmdSnapshotClear:
    def test_clear_prints_count(self, snap_file, capsys):
        add_snapshot("* * * * *", path=snap_file)
        args = _make_args(snapshot_cmd="clear", file=snap_file)
        cmd_snapshot(args)
        out = capsys.readouterr().out
        assert "1" in out


class TestCmdSnapshotCompare:
    def test_compare_shows_expressions(self, snap_file, capsys):
        add_snapshot("0 1 * * *", path=snap_file)
        add_snapshot("0 2 * * *", path=snap_file)
        args = _make_args(snapshot_cmd="compare", index_a=0, index_b=1, file=snap_file)
        cmd_snapshot(args)
        out = capsys.readouterr().out
        assert "0 1 * * *" in out
        assert "0 2 * * *" in out

    def test_compare_out_of_range_exits(self, snap_file):
        add_snapshot("* * * * *", path=snap_file)
        args = _make_args(snapshot_cmd="compare", index_a=0, index_b=5, file=snap_file)
        with pytest.raises(SystemExit):
            cmd_snapshot(args)
