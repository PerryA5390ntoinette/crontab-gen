"""Tests for crontab_gen.search module."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from crontab_gen.search import search, SearchResult, _entry_matches
from crontab_gen.tags import TagEntry


@pytest.fixture()
def sample_entries():
    return [
        TagEntry(expression="0 * * * *", label="hourly", tags=["infra", "frequent"]),
        TagEntry(expression="0 0 * * *", label="midnight", tags=["daily"]),
        TagEntry(expression="*/5 * * * *", label="every 5 mins", tags=["frequent"]),
        TagEntry(expression="0 9 * * 1", label="monday morning", tags=["weekly"]),
    ]


def _patch_tags(entries):
    return patch("crontab_gen.search.all_tags", return_value=entries)


class TestEntryMatches:
    def test_matches_by_expression_substring(self, sample_entries):
        entry = sample_entries[0]  # "0 * * * *"
        assert _entry_matches(entry, "0 *", None) is True

    def test_matches_by_label(self, sample_entries):
        entry = sample_entries[1]  # label="midnight"
        assert _entry_matches(entry, "midnight", None) is True

    def test_no_match_wrong_keyword(self, sample_entries):
        entry = sample_entries[0]
        assert _entry_matches(entry, "zzznomatch", None) is False

    def test_tag_filter_excludes_non_matching(self, sample_entries):
        entry = sample_entries[0]  # tags=["infra", "frequent"]
        assert _entry_matches(entry, "", "daily") is False

    def test_tag_filter_includes_matching(self, sample_entries):
        entry = sample_entries[0]  # tags=["infra", "frequent"]
        assert _entry_matches(entry, "", "frequent") is True

    def test_empty_keyword_and_no_tag_matches_all(self, sample_entries):
        for entry in sample_entries:
            assert _entry_matches(entry, "", None) is True


class TestSearch:
    def test_returns_list(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search()
        assert isinstance(results, list)

    def test_all_returned_without_filters(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search()
        assert len(results) == len(sample_entries)

    def test_keyword_filters_results(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search(keyword="midnight")
        assert len(results) == 1
        assert results[0].expression == "0 0 * * *"

    def test_tag_filter_returns_only_matching(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search(tag="daily")
        assert all("daily" in r.matched_tags for r in results)
        assert len(results) == 1

    def test_tag_frequent_returns_two(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search(tag="frequent")
        assert len(results) == 2

    def test_result_has_description(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search()
        for r in results:
            assert isinstance(r.description, str)
            assert len(r.description) > 0

    def test_invalid_expression_excluded(self):
        bad = [TagEntry(expression="not_valid", label=None, tags=[])]
        with _patch_tags(bad):
            results = search()
        assert results == []

    def test_result_is_search_result_instance(self, sample_entries):
        with _patch_tags(sample_entries):
            results = search()
        for r in results:
            assert isinstance(r, SearchResult)
