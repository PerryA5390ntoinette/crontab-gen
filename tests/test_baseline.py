"""Tests for crontab_gen.baseline."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_gen.baseline import (
    BaselineEntry,
    BaselineComparison,
    clear_baseline,
    compare_to_baseline,
    set_baseline,
)


@pytest.fixture()
def bl_file(tmp_path: Path) -> Path:
    return tmp_path / "baseline.json"


class TestBaselineEntry:
    def test_to_dict_roundtrip(self) -> None:
        entry = BaselineEntry(expression="0 9 * * 1", label="weekly")
        assert BaselineEntry.from_dict(entry.to_dict()) == entry

    def test_label_excluded_when_none(self) -> None:
        entry = BaselineEntry(expression="* * * * *")
        assert "label" not in entry.to_dict()

    def test_label_included_when_set(self) -> None:
        entry = BaselineEntry(expression="* * * * *", label="every minute")
        assert entry.to_dict()["label"] == "every minute"


class TestSetBaseline:
    def test_saves_expression(self, bl_file: Path) -> None:
        set_baseline("0 0 * * *", path=bl_file)
        data = json.loads(bl_file.read_text())
        assert data["expression"] == "0 0 * * *"

    def test_saves_label(self, bl_file: Path) -> None:
        set_baseline("0 0 * * *", label="midnight", path=bl_file)
        data = json.loads(bl_file.read_text())
        assert data["label"] == "midnight"

    def test_invalid_expression_raises(self, bl_file: Path) -> None:
        with pytest.raises(ValueError, match="Invalid"):
            set_baseline("not valid", path=bl_file)

    def test_returns_entry(self, bl_file: Path) -> None:
        entry = set_baseline("*/5 * * * *", path=bl_file)
        assert isinstance(entry, BaselineEntry)
        assert entry.expression == "*/5 * * * *"


class TestCompareToBaseline:
    def test_unchanged_when_same(self, bl_file: Path) -> None:
        set_baseline("0 12 * * *", path=bl_file)
        result = compare_to_baseline("0 12 * * *", path=bl_file)
        assert not result.changed

    def test_changed_when_different(self, bl_file: Path) -> None:
        set_baseline("0 12 * * *", path=bl_file)
        result = compare_to_baseline("0 13 * * *", path=bl_file)
        assert result.changed

    def test_raises_when_no_baseline(self, bl_file: Path) -> None:
        with pytest.raises(FileNotFoundError):
            compare_to_baseline("* * * * *", path=bl_file)

    def test_raises_on_invalid_current(self, bl_file: Path) -> None:
        set_baseline("0 0 * * *", path=bl_file)
        with pytest.raises(ValueError):
            compare_to_baseline("bad expr", path=bl_file)

    def test_str_contains_status(self, bl_file: Path) -> None:
        set_baseline("0 0 * * *", path=bl_file)
        result = compare_to_baseline("0 0 * * *", path=bl_file)
        assert "UNCHANGED" in str(result)

    def test_str_contains_changed(self, bl_file: Path) -> None:
        set_baseline("0 0 * * *", path=bl_file)
        result = compare_to_baseline("*/5 * * * *", path=bl_file)
        assert "CHANGED" in str(result)


class TestClearBaseline:
    def test_returns_true_when_file_exists(self, bl_file: Path) -> None:
        set_baseline("* * * * *", path=bl_file)
        assert clear_baseline(path=bl_file) is True
        assert not bl_file.exists()

    def test_returns_false_when_no_file(self, bl_file: Path) -> None:
        assert clear_baseline(path=bl_file) is False
