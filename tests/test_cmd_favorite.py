"""Tests for crontab_gen.cmd_favorite."""
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from crontab_gen.cmd_favorite import add_favorite_subparser, cmd_favorite
from crontab_gen.favorite import add_favorite, list_favorites


@pytest.fixture
def fav_file(tmp_path) -> Path:
    return tmp_path / "favorites.json"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"file": None, "fav_cmd": "list"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddFavoriteSubparser:
    def test_registers_favorite_command(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_favorite_subparser(sub)
        args = p.parse_args(["favorite", "list"])
        assert args.cmd == "favorite"

    def test_add_subcommand_parsed(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_favorite_subparser(sub)
        args = p.parse_args(["favorite", "add", "* * * * *"])
        assert args.fav_cmd == "add"
        assert args.expression == "* * * * *"

    def test_add_with_label_and_tags(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_favorite_subparser(sub)
        args = p.parse_args(["favorite", "add", "0 9 * * 1", "--label", "Weekly", "--tags", "work"])
        assert args.label == "Weekly"
        assert args.tags == ["work"]

    def test_remove_subcommand_parsed(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_favorite_subparser(sub)
        args = p.parse_args(["favorite", "remove", "* * * * *"])
        assert args.fav_cmd == "remove"

    def test_clear_subcommand_parsed(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        add_favorite_subparser(sub)
        args = p.parse_args(["favorite", "clear"])
        assert args.fav_cmd == "clear"


class TestCmdFavorite:
    def test_add_prints_expression(self, fav_file, capsys):
        args = _make_args(fav_cmd="add", expression="* * * * *", label=None, tags=[], file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "* * * * *" in out

    def test_add_with_label_shown(self, fav_file, capsys):
        args = _make_args(fav_cmd="add", expression="0 0 * * *", label="Midnight", tags=[], file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "Midnight" in out

    def test_list_empty_message(self, fav_file, capsys):
        args = _make_args(fav_cmd="list", file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "No favorites" in out

    def test_list_shows_entries(self, fav_file, capsys):
        add_favorite("0 6 * * *", label="Morning", path=fav_file)
        args = _make_args(fav_cmd="list", file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "0 6 * * *" in out

    def test_remove_existing(self, fav_file, capsys):
        add_favorite("* * * * *", path=fav_file)
        args = _make_args(fav_cmd="remove", expression="* * * * *", file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_not_found(self, fav_file, capsys):
        args = _make_args(fav_cmd="remove", expression="0 0 * * *", file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "No favorite found" in out

    def test_clear_reports_count(self, fav_file, capsys):
        add_favorite("* * * * *", path=fav_file)
        add_favorite("0 0 * * *", path=fav_file)
        args = _make_args(fav_cmd="clear", file=fav_file)
        cmd_favorite(args)
        out = capsys.readouterr().out
        assert "2" in out
