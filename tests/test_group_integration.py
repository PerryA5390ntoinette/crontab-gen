"""Integration tests for the group feature."""
from __future__ import annotations

from pathlib import Path

import pytest

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen.group import add_group, get_group, list_groups, remove_group


@pytest.fixture()
def grp_file(tmp_path: Path) -> Path:
    return tmp_path / "groups.json"


class TestGroupIntegration:
    def test_all_stored_expressions_are_valid(self, grp_file):
        exprs = ["0 0 * * *", "30 6 * * 1-5", "*/15 * * * *"]
        add_group("work", exprs, path=grp_file)
        entry = get_group("work", path=grp_file)
        assert entry is not None
        for expr in entry.expressions:
            assert is_valid(expr), f"{expr!r} should be valid"

    def test_all_stored_expressions_are_explainable(self, grp_file):
        exprs = ["0 9 * * 1", "0 17 * * 5"]
        add_group("standup", exprs, path=grp_file)
        entry = get_group("standup", path=grp_file)
        assert entry is not None
        for expr in entry.expressions:
            result = explain(expr)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_remove_reduces_count(self, grp_file):
        add_group("g1", ["* * * * *"], path=grp_file)
        add_group("g2", ["0 0 * * *"], path=grp_file)
        assert len(list_groups(path=grp_file)) == 2
        remove_group("g1", path=grp_file)
        remaining = list_groups(path=grp_file)
        assert len(remaining) == 1
        assert remaining[0].name == "g2"

    def test_multiple_groups_persist_independently(self, grp_file):
        add_group("a", ["0 1 * * *"], description="group a", path=grp_file)
        add_group("b", ["0 2 * * *"], description="group b", path=grp_file)
        ga = get_group("a", path=grp_file)
        gb = get_group("b", path=grp_file)
        assert ga is not None and ga.description == "group a"
        assert gb is not None and gb.description == "group b"
        assert ga.expressions != gb.expressions
