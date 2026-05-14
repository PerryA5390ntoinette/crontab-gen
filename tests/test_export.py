"""Tests for crontab_gen.export."""
from __future__ import annotations

import json

import pytest

from crontab_gen.export import (
    ExportEntry,
    export_json,
    export_shell,
    export_markdown,
)


class TestExportEntry:
    def test_to_dict_includes_expression(self):
        entry = ExportEntry(expression="* * * * *", description="Every minute")
        d = entry.to_dict()
        assert d["expression"] == "* * * * *"

    def test_to_dict_excludes_none_label(self):
        entry = ExportEntry(expression="* * * * *", description="Every minute")
        assert "label" not in entry.to_dict()

    def test_to_dict_includes_label_when_set(self):
        entry = ExportEntry(expression="* * * * *", description="Every minute", label="heartbeat")
        assert entry.to_dict()["label"] == "heartbeat"


class TestExportJson:
    def test_returns_valid_json(self):
        result = export_json(["* * * * *"])
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1

    def test_contains_expression(self):
        result = json.loads(export_json(["0 * * * *"]))
        assert result[0]["expression"] == "0 * * * *"

    def test_multiple_expressions(self):
        result = json.loads(export_json(["* * * * *", "0 0 * * *"]))
        assert len(result) == 2

    def test_labels_included(self):
        result = json.loads(export_json(["* * * * *"], labels=["ping"]))
        assert result[0]["label"] == "ping"


class TestExportShell:
    def test_contains_expression(self):
        result = export_shell(["0 0 * * *"])
        assert "0 0 * * *" in result

    def test_contains_comment(self):
        result = export_shell(["0 0 * * *"])
        assert result.startswith("#")

    def test_label_used_as_comment(self):
        result = export_shell(["0 0 * * *"], labels=["daily-job"])
        assert "# daily-job" in result

    def test_multiple_entries_separated(self):
        result = export_shell(["* * * * *", "0 0 * * *"])
        assert result.count("/path/to/command") == 2


class TestExportMarkdown:
    def test_has_header_row(self):
        result = export_markdown(["* * * * *"])
        assert "| Expression |" in result

    def test_has_separator_row(self):
        result = export_markdown(["* * * * *"])
        assert "|---|" in result

    def test_expression_in_backticks(self):
        result = export_markdown(["* * * * *"])
        assert "`* * * * *`" in result

    def test_label_in_row(self):
        result = export_markdown(["0 0 * * *"], labels=["nightly"])
        assert "nightly" in result
