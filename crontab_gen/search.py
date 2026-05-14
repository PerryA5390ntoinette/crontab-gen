"""Search/filter cron expressions by keyword, tag, or field pattern."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen.tags import all_tags, TagEntry


@dataclass
class SearchResult:
    expression: str
    label: Optional[str]
    description: str
    matched_tags: List[str]

    def __str__(self) -> str:
        parts = [self.expression]
        if self.label:
            parts.append(f"({self.label})")
        parts.append("-", self.description)
        return " ".join(parts)


def _entry_matches(entry: TagEntry, keyword: str, tag: Optional[str]) -> bool:
    """Return True if the entry matches the given keyword and/or tag filter."""
    keyword_lower = keyword.lower() if keyword else ""
    if tag and tag.lower() not in [t.lower() for t in entry.tags]:
        return False
    if keyword_lower:
        if keyword_lower in entry.expression.lower():
            return True
        if entry.label and keyword_lower in entry.label.lower():
            return True
        description = explain(entry.expression)
        if keyword_lower in description.lower():
            return True
        return False
    return True


def search(
    keyword: str = "",
    tag: Optional[str] = None,
    history_file: Optional[str] = None,
    tags_file: Optional[str] = None,
) -> List[SearchResult]:
    """Search saved tagged expressions by keyword and/or tag."""
    entries: List[TagEntry] = all_tags(path=tags_file)
    results: List[SearchResult] = []
    for entry in entries:
        if not is_valid(entry.expression):
            continue
        if _entry_matches(entry, keyword, tag):
            description = explain(entry.expression)
            results.append(
                SearchResult(
                    expression=entry.expression,
                    label=entry.label,
                    description=description,
                    matched_tags=list(entry.tags),
                )
            )
    return results
