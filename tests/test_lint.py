"""Tests for crontab_gen.lint module."""

import pytest

from crontab_gen.lint import LintWarning, LintResult, lint


class TestLintResult:
    def test_ok_when_no_warnings(self):
        result = LintResult(expression="0 * * * *")
        assert result.ok is True

    def test_not_ok_when_warnings_present(self):
        result = LintResult(
            expression="bad",
            warnings=[LintWarning("expression", "invalid")],
        )
        assert result.ok is False

    def test_str_ok(self):
        result = LintResult(expression="0 * * * *")
        assert "No issues" in str(result)

    def test_str_with_warnings(self):
        result = LintResult(
            expression="* * * * *",
            warnings=[LintWarning("minute/hour", "runs every minute")],
        )
        text = str(result)
        assert "Lint results" in text
        assert "minute/hour" in text


class TestLintInvalidExpression:
    def test_invalid_expression_returns_warning(self):
        result = lint("not a cron")
        assert not result.ok
        assert any(w.field == "expression" for w in result.warnings)


class TestLintRedundantStep:
    def test_star_slash_one_flagged(self):
        result = lint("*/1 * * * *")
        assert any("redundant" in w.message for w in result.warnings)

    def test_normal_step_not_flagged(self):
        result = lint("*/5 * * * *")
        assert not any("redundant" in w.message for w in result.warnings)


class TestLintDomDowConflict:
    def test_both_restricted_warns(self):
        result = lint("0 12 1 * 1")
        assert any("dom/dow" in w.field for w in result.warnings)

    def test_only_dom_restricted_ok(self):
        result = lint("0 12 1 * *")
        assert not any("dom/dow" in w.field for w in result.warnings)

    def test_only_dow_restricted_ok(self):
        result = lint("0 12 * * 1")
        assert not any("dom/dow" in w.field for w in result.warnings)


class TestLintHighFrequency:
    def test_every_minute_warns(self):
        result = lint("* * * * *")
        assert any("every minute" in w.message for w in result.warnings)

    def test_specific_minute_no_warn(self):
        result = lint("0 * * * *")
        assert not any("every minute" in w.message for w in result.warnings)


class TestLintCleanExpression:
    def test_clean_expression_has_no_warnings(self):
        result = lint("30 6 * * 1-5")
        assert result.ok

    def test_str_severity_included(self):
        w = LintWarning("minute", "test msg", severity="info")
        assert "INFO" in str(w)
