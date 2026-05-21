"""Tests for crontab_gen.digest."""
import json
import pytest
from pathlib import Path

from crontab_gen.digest import build_digest, DigestEntry, Digest


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_history(path: Path, expressions):
    entries = [{"expression": e, "created_at": "2024-01-01T00:00:00"} for e in expressions]
    path.write_text(json.dumps(entries))


def _write_bookmarks(path: Path, expressions):
    entries = [{"expression": e, "created_at": "2024-01-01T00:00:00"} for e in expressions]
    path.write_text(json.dumps(entries))


def _write_tags(path: Path, expressions):
    entries = [{"expression": e, "tag": "test", "created_at": "2024-01-01T00:00:00"} for e in expressions]
    path.write_text(json.dumps(entries))


# ---------------------------------------------------------------------------
# DigestEntry
# ---------------------------------------------------------------------------

class TestDigestEntry:
    def test_str_contains_expression(self):
        e = DigestEntry(expression="* * * * *", description="every minute", sources=["history"])
        assert "* * * * *" in str(e)

    def test_str_contains_source(self):
        e = DigestEntry(expression="0 * * * *", description="every hour", sources=["bookmark"])
        assert "bookmark" in str(e)

    def test_str_contains_description(self):
        e = DigestEntry(expression="0 0 * * *", description="daily", sources=["tags"])
        assert "daily" in str(e)

    def test_multiple_sources_shown(self):
        e = DigestEntry(expression="* * * * *", description="every minute", sources=["history", "bookmark"])
        text = str(e)
        assert "history" in text
        assert "bookmark" in text


# ---------------------------------------------------------------------------
# Digest
# ---------------------------------------------------------------------------

class TestDigest:
    def test_str_shows_count(self):
        d = Digest(entries=[], total_unique=0)
        assert "0" in str(d)

    def test_str_lists_entries(self):
        e = DigestEntry(expression="* * * * *", description="every minute", sources=["history"])
        d = Digest(entries=[e], total_unique=1)
        assert "* * * * *" in str(d)


# ---------------------------------------------------------------------------
# build_digest
# ---------------------------------------------------------------------------

class TestBuildDigest:
    def test_empty_stores_give_empty_digest(self, tmp_path):
        h = tmp_path / "history.json"
        b = tmp_path / "bookmarks.json"
        t = tmp_path / "tags.json"
        h.write_text("[]")
        b.write_text("[]")
        t.write_text("[]")
        d = build_digest(str(h), str(b), str(t))
        assert d.total_unique == 0
        assert d.entries == []

    def test_unique_expressions_counted(self, tmp_path):
        h = tmp_path / "history.json"
        b = tmp_path / "bookmarks.json"
        t = tmp_path / "tags.json"
        _write_history(h, ["* * * * *", "0 * * * *"])
        _write_bookmarks(b, ["0 0 * * *"])
        t.write_text("[]")
        d = build_digest(str(h), str(b), str(t))
        assert d.total_unique == 3

    def test_duplicate_across_stores_merged(self, tmp_path):
        h = tmp_path / "history.json"
        b = tmp_path / "bookmarks.json"
        t = tmp_path / "tags.json"
        _write_history(h, ["* * * * *"])
        _write_bookmarks(b, ["* * * * *"])
        t.write_text("[]")
        d = build_digest(str(h), str(b), str(t))
        assert d.total_unique == 1
        assert set(d.entries[0].sources) == {"history", "bookmark"}

    def test_invalid_expressions_excluded(self, tmp_path):
        h = tmp_path / "history.json"
        b = tmp_path / "bookmarks.json"
        t = tmp_path / "tags.json"
        _write_history(h, ["not_a_cron"])
        b.write_text("[]")
        t.write_text("[]")
        d = build_digest(str(h), str(b), str(t))
        assert d.total_unique == 0

    def test_entries_sorted_by_expression(self, tmp_path):
        h = tmp_path / "history.json"
        b = tmp_path / "bookmarks.json"
        t = tmp_path / "tags.json"
        _write_history(h, ["0 12 * * *", "* * * * *", "0 0 * * 1"])
        b.write_text("[]")
        t.write_text("[]")
        d = build_digest(str(h), str(b), str(t))
        exprs = [e.expression for e in d.entries]
        assert exprs == sorted(exprs)
