"""Tests for crontab_gen.favorite."""
import pytest
from pathlib import Path
from crontab_gen.favorite import (
    FavoriteEntry,
    add_favorite,
    list_favorites,
    remove_favorite,
    clear_favorites,
)


@pytest.fixture
def fav_file(tmp_path) -> Path:
    return tmp_path / "favorites.json"


class TestFavoriteEntry:
    def test_to_dict_roundtrip(self):
        e = FavoriteEntry(expression="0 * * * *", label="Hourly", tags=["work"])
        d = e.to_dict()
        restored = FavoriteEntry.from_dict(d)
        assert restored.expression == e.expression
        assert restored.label == e.label
        assert restored.tags == e.tags

    def test_label_excluded_when_none(self):
        e = FavoriteEntry(expression="* * * * *")
        assert "label" not in e.to_dict()

    def test_label_included_when_set(self):
        e = FavoriteEntry(expression="* * * * *", label="Every minute")
        assert e.to_dict()["label"] == "Every minute"

    def test_tags_excluded_when_empty(self):
        e = FavoriteEntry(expression="* * * * *")
        assert "tags" not in e.to_dict()

    def test_created_at_is_set(self):
        e = FavoriteEntry(expression="* * * * *")
        assert e.created_at is not None


class TestAddFavorite:
    def test_adds_entry(self, fav_file):
        add_favorite("0 9 * * 1", path=fav_file)
        entries = list_favorites(path=fav_file)
        assert len(entries) == 1
        assert entries[0].expression == "0 9 * * 1"

    def test_returns_entry(self, fav_file):
        entry = add_favorite("5 4 * * *", label="Daily", path=fav_file)
        assert entry.expression == "5 4 * * *"
        assert entry.label == "Daily"

    def test_multiple_entries(self, fav_file):
        add_favorite("* * * * *", path=fav_file)
        add_favorite("0 0 * * *", path=fav_file)
        assert len(list_favorites(path=fav_file)) == 2


class TestRemoveFavorite:
    def test_removes_existing(self, fav_file):
        add_favorite("* * * * *", path=fav_file)
        result = remove_favorite("* * * * *", path=fav_file)
        assert result is True
        assert list_favorites(path=fav_file) == []

    def test_returns_false_when_not_found(self, fav_file):
        result = remove_favorite("0 0 * * *", path=fav_file)
        assert result is False

    def test_only_removes_matching(self, fav_file):
        add_favorite("* * * * *", path=fav_file)
        add_favorite("0 0 * * *", path=fav_file)
        remove_favorite("* * * * *", path=fav_file)
        remaining = list_favorites(path=fav_file)
        assert len(remaining) == 1
        assert remaining[0].expression == "0 0 * * *"


class TestClearFavorites:
    def test_clears_all(self, fav_file):
        add_favorite("* * * * *", path=fav_file)
        add_favorite("0 0 * * *", path=fav_file)
        count = clear_favorites(path=fav_file)
        assert count == 2
        assert list_favorites(path=fav_file) == []

    def test_clear_empty_returns_zero(self, fav_file):
        assert clear_favorites(path=fav_file) == 0
