"""Tests for crontab_gen.rating."""
from __future__ import annotations

import pytest
from pathlib import Path

from crontab_gen.rating import (
    RatingEntry,
    add_rating,
    get_rating,
    list_ratings,
    remove_rating,
)


@pytest.fixture
def rat_file(tmp_path: Path) -> Path:
    return tmp_path / "ratings.json"


class TestRatingEntry:
    def test_to_dict_roundtrip(self):
        entry = RatingEntry(expression="* * * * *", score=4, label="every minute")
        d = entry.to_dict()
        restored = RatingEntry.from_dict(d)
        assert restored.expression == entry.expression
        assert restored.score == entry.score
        assert restored.label == entry.label

    def test_label_excluded_when_none(self):
        entry = RatingEntry(expression="0 * * * *", score=3)
        assert "label" not in entry.to_dict()

    def test_label_included_when_set(self):
        entry = RatingEntry(expression="0 * * * *", score=3, label="hourly")
        assert entry.to_dict()["label"] == "hourly"


class TestAddRating:
    def test_add_returns_entry(self, rat_file):
        entry = add_rating("* * * * *", 5, path=rat_file)
        assert entry.score == 5
        assert entry.expression == "* * * * *"

    def test_invalid_score_raises(self, rat_file):
        with pytest.raises(ValueError):
            add_rating("* * * * *", 0, path=rat_file)

    def test_score_too_high_raises(self, rat_file):
        with pytest.raises(ValueError):
            add_rating("* * * * *", 6, path=rat_file)

    def test_persists_to_file(self, rat_file):
        add_rating("0 12 * * *", 4, path=rat_file)
        entries = list_ratings(rat_file)
        assert len(entries) == 1
        assert entries[0].score == 4

    def test_overwrites_existing_rating(self, rat_file):
        add_rating("* * * * *", 3, path=rat_file)
        add_rating("* * * * *", 5, path=rat_file)
        entries = list_ratings(rat_file)
        assert len(entries) == 1
        assert entries[0].score == 5

    def test_with_label(self, rat_file):
        entry = add_rating("0 0 * * *", 5, label="daily midnight", path=rat_file)
        assert entry.label == "daily midnight"


class TestGetRating:
    def test_returns_none_when_missing(self, rat_file):
        assert get_rating("* * * * *", rat_file) is None

    def test_returns_entry_when_present(self, rat_file):
        add_rating("0 6 * * *", 4, path=rat_file)
        entry = get_rating("0 6 * * *", rat_file)
        assert entry is not None
        assert entry.score == 4


class TestRemoveRating:
    def test_remove_existing_returns_true(self, rat_file):
        add_rating("* * * * *", 3, path=rat_file)
        assert remove_rating("* * * * *", rat_file) is True

    def test_remove_missing_returns_false(self, rat_file):
        assert remove_rating("* * * * *", rat_file) is False

    def test_remove_reduces_count(self, rat_file):
        add_rating("* * * * *", 3, path=rat_file)
        add_rating("0 * * * *", 4, path=rat_file)
        remove_rating("* * * * *", rat_file)
        assert len(list_ratings(rat_file)) == 1
