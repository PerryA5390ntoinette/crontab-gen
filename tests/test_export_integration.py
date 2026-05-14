"""Integration tests verifying export round-trips through the full pipeline."""
from __future__ import annotations

import json

import pytest

from crontab_gen.export import export_json, export_shell, export_markdown
from crontab_gen.expression import CronExpression
from crontab_gen.explainer import explain


EXPRESSIONS = [
    "* * * * *",
    "0 0 * * *",
    "*/5 * * * *",
    "0 9-17 * * 1-5",
]


class TestJsonRoundtrip:
    def test_all_expressions_present(self):
        result = json.loads(export_json(EXPRESSIONS))
        exported = [r["expression"] for r in result]
        assert exported == EXPRESSIONS

    def test_descriptions_are_non_empty(self):
        result = json.loads(export_json(EXPRESSIONS))
        for entry in result:
            assert entry["description"], f"Empty description for {entry['expression']}"

    def test_description_matches_explainer(self):
        for expr in EXPRESSIONS:
            result = json.loads(export_json([expr]))
            expected = explain(CronExpression(expr))
            assert result[0]["description"] == expected


class TestShellRoundtrip:
    def test_all_expressions_in_output(self):
        result = export_shell(EXPRESSIONS)
        for expr in EXPRESSIONS:
            assert expr in result

    def test_command_count_matches(self):
        result = export_shell(EXPRESSIONS)
        assert result.count("/path/to/command") == len(EXPRESSIONS)

    def test_comment_lines_present(self):
        result = export_shell(EXPRESSIONS)
        comment_lines = [l for l in result.splitlines() if l.startswith("#")]
        assert len(comment_lines) == len(EXPRESSIONS)


class TestMarkdownRoundtrip:
    def test_all_expressions_in_table(self):
        result = export_markdown(EXPRESSIONS)
        for expr in EXPRESSIONS:
            assert expr in result

    def test_row_count_matches(self):
        result = export_markdown(EXPRESSIONS)
        # header + separator + data rows
        data_rows = [
            l for l in result.splitlines()
            if l.startswith("|") and not l.startswith("|---") and "Expression" not in l
        ]
        assert len(data_rows) == len(EXPRESSIONS)
