"""Integration tests: favorites round-trip through add/list/remove."""
import pytest
from pathlib import Path
from crontab_gen.favorite import add_favorite, list_favorites, remove_favorite
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain


@pytest.fixture
def fav_file(tmp_path) -> Path:
    return tmp_path / "fav_integration.json"


EXPRESSIONS = [
    "* * * * *",
    "0 9 * * 1-5",
    "30 18 1 * *",
    "0 0 * * 0",
    "*/15 * * * *",
]


class TestFavoriteIntegration:
    def test_all_saved_expressions_are_valid(self, fav_file):
        for expr in EXPRESSIONS:
            add_favorite(expr, path=fav_file)
        entries = list_favorites(path=fav_file)
        for entry in entries:
            assert is_valid(entry.expression), f"Invalid: {entry.expression}"

    def test_all_favorites_are_explainable(self, fav_file):
        for expr in EXPRESSIONS:
            add_favorite(expr, path=fav_file)
        for entry in list_favorites(path=fav_file):
            result = explain(entry.expression)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_remove_reduces_count(self, fav_file):
        for expr in EXPRESSIONS:
            add_favorite(expr, path=fav_file)
        initial = len(list_favorites(path=fav_file))
        remove_favorite(EXPRESSIONS[0], path=fav_file)
        assert len(list_favorites(path=fav_file)) == initial - 1

    def test_tags_preserved_after_reload(self, fav_file):
        add_favorite("0 9 * * 1", tags=["work", "morning"], path=fav_file)
        entries = list_favorites(path=fav_file)
        assert entries[0].tags == ["work", "morning"]

    def test_label_preserved_after_reload(self, fav_file):
        add_favorite("0 0 1 1 *", label="New Year", path=fav_file)
        entries = list_favorites(path=fav_file)
        assert entries[0].label == "New Year"

    def test_duplicate_expression_not_added_twice(self, fav_file):
        """Adding the same expression twice should not create duplicate entries."""
        expr = "0 12 * * *"
        add_favorite(expr, path=fav_file)
        add_favorite(expr, path=fav_file)
        entries = list_favorites(path=fav_file)
        matching = [e for e in entries if e.expression == expr]
        assert len(matching) == 1, (
            f"Expected 1 entry for '{expr}', found {len(matching)}"
        )
