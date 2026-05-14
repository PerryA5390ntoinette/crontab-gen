import argparse
import pytest
from unittest.mock import patch, MagicMock
from crontab_gen.cmd_lint import add_lint_subparser, cmd_lint


def _make_args(**kwargs):
    defaults = {
        "expression": "* * * * *",
        "no_history": False,
        "func": cmd_lint,
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    return ns


class TestAddLintSubparser:
    def test_registers_lint_command(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_lint_subparser(sub)
        args = parser.parse_args(["lint", "* * * * *"])
        assert args.func is cmd_lint

    def test_no_history_flag_default_false(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_lint_subparser(sub)
        args = parser.parse_args(["lint", "* * * * *"])
        assert args.no_history is False

    def test_no_history_flag_can_be_set(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_lint_subparser(sub)
        args = parser.parse_args(["lint", "* * * * *", "--no-history"])
        assert args.no_history is True


class TestCmdLint:
    def test_invalid_expression_returns_2(self, capsys):
        args = _make_args(expression="not valid at all")
        code = cmd_lint(args)
        assert code == 2
        captured = capsys.readouterr()
        assert "not a valid cron expression" in captured.out

    def test_clean_expression_returns_0(self, capsys):
        args = _make_args(expression="0 9 * * 1-5", no_history=True)
        code = cmd_lint(args)
        assert code == 0

    def test_lint_result_printed(self, capsys):
        args = _make_args(expression="* * * * *", no_history=True)
        cmd_lint(args)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_history_recorded_by_default(self):
        args = _make_args(expression="0 0 * * *", no_history=False)
        with patch("crontab_gen.cmd_lint.add_entry") as mock_add:
            cmd_lint(args)
            mock_add.assert_called_once_with("0 0 * * *", command="lint")

    def test_history_skipped_with_flag(self):
        args = _make_args(expression="0 0 * * *", no_history=True)
        with patch("crontab_gen.cmd_lint.add_entry") as mock_add:
            cmd_lint(args)
            mock_add.assert_not_called()

    def test_warnings_return_1(self, capsys):
        from crontab_gen.lint import LintResult, LintWarning
        mock_result = LintResult(warnings=[LintWarning(field="minute", message="test warning")])
        args = _make_args(expression="* * * * *", no_history=True)
        with patch("crontab_gen.cmd_lint.lint", return_value=mock_result):
            code = cmd_lint(args)
        assert code == 1
