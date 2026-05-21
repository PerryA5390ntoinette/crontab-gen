"""Detect scheduling conflicts between multiple cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .next_run import next_runs
from .expression import is_valid


@dataclass
class ConflictPair:
    expr_a: str
    expr_b: str
    shared_times: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        times = ", ".join(self.shared_times[:3])
        suffix = f" (+{len(self.shared_times) - 3} more)" if len(self.shared_times) > 3 else ""
        return (
            f"CONFLICT: '{self.expr_a}' vs '{self.expr_b}'\n"
            f"  Shared times: {times}{suffix}"
        )


@dataclass
class ConflictResult:
    expressions: List[str]
    pairs: List[ConflictPair] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.pairs)

    def __str__(self) -> str:  # pragma: no cover
        if not self.has_conflicts:
            return "No conflicts detected among the given expressions."
        lines = [f"{len(self.pairs)} conflict(s) found:"]
        for pair in self.pairs:
            lines.append(str(pair))
        return "\n".join(lines)


def _shared_times(expr_a: str, expr_b: str, horizon: int = 60) -> List[str]:
    """Return ISO-formatted datetimes where both expressions fire within *horizon* runs."""
    runs_a = {dt.replace(second=0, microsecond=0) for dt in next_runs(expr_a, horizon)}
    runs_b = {dt.replace(second=0, microsecond=0) for dt in next_runs(expr_b, horizon)}
    shared = sorted(runs_a & runs_b)
    return [dt.strftime("%Y-%m-%d %H:%M") for dt in shared]


def detect_conflicts(expressions: List[str], horizon: int = 60) -> ConflictResult:
    """Check every pair of expressions for scheduling conflicts.

    Args:
        expressions: List of cron expression strings.
        horizon:     Number of upcoming runs to sample per expression.

    Raises:
        ValueError: If any expression is invalid.
    """
    for expr in expressions:
        if not is_valid(expr):
            raise ValueError(f"Invalid cron expression: '{expr}'")

    pairs: List[ConflictPair] = []
    exprs = list(expressions)
    for i in range(len(exprs)):
        for j in range(i + 1, len(exprs)):
            shared = _shared_times(exprs[i], exprs[j], horizon)
            if shared:
                pairs.append(ConflictPair(exprs[i], exprs[j], shared))

    return ConflictResult(expressions=exprs, pairs=pairs)
