"""Tests for crontab_gen.streak."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from crontab_gen.streak import (
    StreakEntry,
    all_streaks,
    get_streak,
    record,
)


@pytest.fixture()
def streak_file(tmp_path: Path) -> Path:
    return tmp_path / "streaks.json"


class TestStreakEntry:
    def test_to_dict_roundtrip(self):
        entry = StreakEntry(expression="0 * * * *", dates=["2024-01-01"])
        restored = StreakEntry.from_dict(entry.to_dict())
        assert restored.expression == entry.expression
        assert restored.dates == entry.dates

    def test_record_today_adds_date(self):
        entry = StreakEntry(expression="* * * * *")
        entry.record_today()
        assert date.today().isoformat() in entry.dates

    def test_record_today_is_idempotent(self):
        entry = StreakEntry(expression="* * * * *")
        entry.record_today()
        entry.record_today()
        assert entry.dates.count(date.today().isoformat()) == 1

    def test_current_streak_empty(self):
        entry = StreakEntry(expression="* * * * *")
        assert entry.current_streak == 0

    def test_current_streak_today_only(self):
        entry = StreakEntry(expression="* * * * *")
        entry.record_today()
        assert entry.current_streak == 1

    def test_current_streak_consecutive_days(self):
        today = date.today()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(3)]
        entry = StreakEntry(expression="* * * * *", dates=dates)
        assert entry.current_streak == 3

    def test_current_streak_broken(self):
        today = date.today()
        dates = [
            today.isoformat(),
            (today - timedelta(days=2)).isoformat(),
        ]
        entry = StreakEntry(expression="* * * * *", dates=dates)
        assert entry.current_streak == 1

    def test_current_streak_stale(self):
        old = (date.today() - timedelta(days=5)).isoformat()
        entry = StreakEntry(expression="* * * * *", dates=[old])
        assert entry.current_streak == 0

    def test_longest_streak(self):
        today = date.today()
        dates = [
            (today - timedelta(days=10)).isoformat(),
            (today - timedelta(days=9)).isoformat(),
            (today - timedelta(days=8)).isoformat(),
            today.isoformat(),
        ]
        entry = StreakEntry(expression="* * * * *", dates=dates)
        assert entry.longest_streak == 3


class TestRecordAndRetrieve:
    def test_record_creates_entry(self, streak_file):
        entry = record("0 12 * * *", path=streak_file)
        assert entry.expression == "0 12 * * *"
        assert len(entry.dates) == 1

    def test_record_updates_existing(self, streak_file):
        record("0 12 * * *", path=streak_file)
        record("0 12 * * *", path=streak_file)
        entry = get_streak("0 12 * * *", path=streak_file)
        assert len(entry.dates) == 1  # idempotent for same day

    def test_get_streak_unknown_returns_none(self, streak_file):
        assert get_streak("1 2 3 4 5", path=streak_file) is None

    def test_all_streaks_returns_all(self, streak_file):
        record("* * * * *", path=streak_file)
        record("0 0 * * *", path=streak_file)
        entries = all_streaks(path=streak_file)
        expressions = [e.expression for e in entries]
        assert "* * * * *" in expressions
        assert "0 0 * * *" in expressions

    def test_all_streaks_empty_file(self, streak_file):
        assert all_streaks(path=streak_file) == []
