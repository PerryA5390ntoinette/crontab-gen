"""Integration tests for priority module — validates stored expressions."""
import pytest
from pathlib import Path

from crontab_gen.priority import add_priority, list_priorities, remove_priority, LEVELS
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain


@pytest.fixture
def pri_file(tmp_path) -> Path:
    return tmp_path / "priorities.json"


EXPRESSIONS = [
    ("* * * * *", "low"),
    ("0 * * * *", "medium"),
    ("0 6 * * 1", "high"),
    ("30 4 1 * *", "critical"),
]


class TestPriorityIntegration:
    def test_all_stored_expressions_are_valid(self, pri_file):
        for expr, level in EXPRESSIONS:
            add_priority(expr, level, path=pri_file)
        for entry in list_priorities(path=pri_file):
            assert is_valid(entry.expression), f"Invalid: {entry.expression}"

    def test_all_stored_expressions_are_explainable(self, pri_file):
        for expr, level in EXPRESSIONS:
            add_priority(expr, level, path=pri_file)
        for entry in list_priorities(path=pri_file):
            result = explain(entry.expression)
            assert result and len(result) > 0

    def test_remove_reduces_count(self, pri_file):
        for expr, level in EXPRESSIONS:
            add_priority(expr, level, path=pri_file)
        initial = len(list_priorities(path=pri_file))
        remove_priority(EXPRESSIONS[0][0], path=pri_file)
        assert len(list_priorities(path=pri_file)) == initial - 1

    def test_level_filter_is_consistent(self, pri_file):
        for expr, level in EXPRESSIONS:
            add_priority(expr, level, path=pri_file)
        for lvl in LEVELS:
            filtered = list_priorities(level=lvl, path=pri_file)
            assert all(e.level == lvl for e in filtered)

    def test_all_levels_accepted(self, pri_file):
        for i, lvl in enumerate(LEVELS):
            add_priority(f"0 {i} * * *", lvl, path=pri_file)
        assert len(list_priorities(path=pri_file)) == len(LEVELS)
