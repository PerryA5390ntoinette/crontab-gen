"""Weekly digest: summarise stored expressions across tags, bookmarks, and history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_gen import history, bookmark, tags
from crontab_gen.explainer import explain
from crontab_gen.expression import is_valid


@dataclass
class DigestEntry:
    expression: str
    description: str
    sources: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        src = ", ".join(sorted(self.sources))
        return f"{self.expression!r:30s}  [{src}]  {self.description}"


@dataclass
class Digest:
    entries: List[DigestEntry] = field(default_factory=list)
    total_unique: int = 0

    def __str__(self) -> str:
        lines = [f"Digest — {self.total_unique} unique expression(s):", ""]
        for e in self.entries:
            lines.append(f"  {e}")
        return "\n".join(lines)


def _collect(
    history_path: str | None = None,
    bookmark_path: str | None = None,
    tags_path: str | None = None,
) -> dict[str, DigestEntry]:
    """Collect expressions from all stores, keyed by expression string."""
    seen: dict[str, DigestEntry] = {}

    def _add(expr: str, source: str) -> None:
        if not is_valid(expr):
            return
        if expr not in seen:
            seen[expr] = DigestEntry(
                expression=expr,
                description=explain(expr),
                sources=[],
            )
        if source not in seen[expr].sources:
            seen[expr].sources.append(source)

    kwargs_h = {"path": history_path} if history_path else {}
    for entry in history._load(**kwargs_h):
        _add(entry.expression, "history")

    kwargs_b = {"path": bookmark_path} if bookmark_path else {}
    for entry in bookmark._load(**kwargs_b):
        _add(entry.expression, "bookmark")

    kwargs_t = {"path": tags_path} if tags_path else {}
    for entry in tags._load(**kwargs_t):
        _add(entry.expression, "tags")

    return seen


def build_digest(
    history_path: str | None = None,
    bookmark_path: str | None = None,
    tags_path: str | None = None,
) -> Digest:
    """Build a Digest summarising all known expressions."""
    seen = _collect(history_path, bookmark_path, tags_path)
    entries = sorted(seen.values(), key=lambda e: e.expression)
    return Digest(entries=entries, total_unique=len(entries))
