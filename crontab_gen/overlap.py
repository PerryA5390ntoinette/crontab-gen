"""Detect overlapping cron expressions that fire at the same time."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .next_run import next_runs
from .expression import is_valid


@dataclass
class OverlapResult:
    expr_a: str
    expr_b: str
    shared_times: List[str] = field(default_factory=list)

    @property
    def has_overlap(self) -> bool:
        return len(self.shared_times) > 0

    def __str__(self) -> str:
        if not self.has_overlap:
            return f"No overlap detected between '{self.expr_a}' and '{self.expr_b}'."
        times = ", ".join(self.shared_times[:5])
        more = f" (+{len(self.shared_times) - 5} more)" if len(self.shared_times) > 5 else ""
        return (
            f"Overlap between '{self.expr_a}' and '{self.expr_b}': "
            f"{len(self.shared_times)} shared run(s) — {times}{more}"
        )


def _fmt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def detect_overlap(
    expr_a: str,
    expr_b: str,
    *,
    lookahead: int = 100,
) -> OverlapResult:
    """Return an OverlapResult describing shared fire times between two expressions.

    Args:
        expr_a: First cron expression.
        expr_b: Second cron expression.
        lookahead: Number of upcoming runs to sample per expression.

    Raises:
        ValueError: If either expression is invalid.
    """
    for expr in (expr_a, expr_b):
        if not is_valid(expr):
            raise ValueError(f"Invalid cron expression: '{expr}'")

    times_a = {_fmt(dt) for dt in next_runs(expr_a, lookahead)}
    times_b = {_fmt(dt) for dt in next_runs(expr_b, lookahead)}
    shared = sorted(times_a & times_b)
    return OverlapResult(expr_a=expr_a, expr_b=expr_b, shared_times=shared)


def overlap_matrix(
    expressions: List[str],
    *,
    lookahead: int = 100,
) -> List[Tuple[str, str, int]]:
    """Return a list of (expr_a, expr_b, overlap_count) for all pairs with overlap."""
    results = []
    for i, a in enumerate(expressions):
        for b in expressions[i + 1 :]:
            res = detect_overlap(a, b, lookahead=lookahead)
            if res.has_overlap:
                results.append((a, b, len(res.shared_times)))
    return results
