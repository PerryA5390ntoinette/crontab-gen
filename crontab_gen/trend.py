"""Analyse expression usage trends from history."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Tuple

from crontab_gen.history import _load as _load_history


@dataclass
class TrendEntry:
    expression: str
    count: int
    last_used: str  # ISO-format timestamp string

    def __str__(self) -> str:
        return f"{self.expression!r:30s}  runs={self.count}  last={self.last_used}"


@dataclass
class TrendReport:
    entries: List[TrendEntry] = field(default_factory=list)

    def top(self, n: int = 5) -> List[TrendEntry]:
        """Return the *n* most-used expressions."""
        return sorted(self.entries, key=lambda e: e.count, reverse=True)[:n]

    def __str__(self) -> str:
        if not self.entries:
            return "No history data available."
        lines = ["Expression usage trends:", ""]
        for entry in self.top(10):
            lines.append(f"  {entry}")
        return "\n".join(lines)


def build_trend(history_path: str | None = None) -> TrendReport:
    """Build a TrendReport from the persisted history entries."""
    entries = _load_history(history_path)
    if not entries:
        return TrendReport()

    counter: Counter[str] = Counter()
    last_seen: dict[str, str] = {}

    for entry in entries:
        expr = entry.expression
        counter[expr] += 1
        ts = entry.created_at
        if expr not in last_seen or ts > last_seen[expr]:
            last_seen[expr] = ts

    trend_entries = [
        TrendEntry(expression=expr, count=cnt, last_used=last_seen[expr])
        for expr, cnt in counter.items()
    ]
    return TrendReport(entries=trend_entries)


def top_expressions(n: int = 5, history_path: str | None = None) -> List[Tuple[str, int]]:
    """Convenience helper – returns (expression, count) pairs for the top *n*."""
    report = build_trend(history_path)
    return [(e.expression, e.count) for e in report.top(n)]
