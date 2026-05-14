"""Tests for crontab_gen.cmd_template module."""
import argparse
import sys

import pytest

from crontab_gen.cmd_template import add_template_subparser, cmd_template
from crontab_gen.template import save_template


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"template_cmd": "list"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddTemplateSubparser:
    def test_registers_template_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_template_subparser(sub)
        args = parser.parse_args(["template", "list"])
        assert args.command == "template"

    def test_save_subcommand_parsed(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_template_subparser(sub)
        args = parser.parse_args(["template", "save", "myjob", "0 0 * * *"])
        assert args.template_cmd == "save"
        assert args.name == "myjob"
        assert args.expression == "0 0 * * *"

    def test_save_with_tags_and_description(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_template_subparser(sub)
        args = parser.parse_args(["template", "save", "myjob", "0 0 * * *", "-d", "desc", "-t", "prod"])
        assert args.description == "desc"
        assert "prod" in args.tags


class TestCmdTemplateSave:
    def test_save_valid_expression(self, tmp_path, monkeypatch, capsys):
        tpl_file = str(tmp_path / "t.json")
        import crontab_gen.cmd_template as ct
        monkeypatch.setattr(ct, "save_template", lambda **kw: save_template(**kw, path=tpl_file))
        args = _make_args(template_cmd="save", name="j", expression="0 6 * * *", description="", tags=[])
        # patch save_template path directly via module-level call
        from crontab_gen import template as tmod
        original = tmod.DEFAULT_TEMPLATE_FILE
        tmod.DEFAULT_TEMPLATE_FILE = tpl_file
        cmd_template(args)
        tmod.DEFAULT_TEMPLATE_FILE = original
        out = capsys.readouterr().out
        assert "saved" in out

    def test_save_invalid_expression_exits(self, capsys):
        args = _make_args(template_cmd="save", name="bad", expression="not a cron", description="", tags=[])
        with pytest.raises(SystemExit) as exc:
            cmd_template(args)
        assert exc.value.code == 1


class TestCmdTemplateList:
    def test_list_empty(self, tmp_path, monkeypatch, capsys):
        tpl_file = str(tmp_path / "t.json")
        from crontab_gen import template as tmod
        tmod.DEFAULT_TEMPLATE_FILE = tpl_file
        args = _make_args(template_cmd="list")
        cmd_template(args)
        out = capsys.readouterr().out
        assert "No templates" in out


class TestCmdTemplateDelete:
    def test_delete_missing_exits(self, tmp_path, monkeypatch, capsys):
        tpl_file = str(tmp_path / "t.json")
        from crontab_gen import template as tmod
        tmod.DEFAULT_TEMPLATE_FILE = tpl_file
        args = _make_args(template_cmd="delete", name="ghost")
        with pytest.raises(SystemExit) as exc:
            cmd_template(args)
        assert exc.value.code == 1
