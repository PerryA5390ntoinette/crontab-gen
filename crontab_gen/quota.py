"""Quota tracking: warn when a cron expression fires too many times in a window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class QuotaWarning:
    expression: str
    window_hours: int
    limit: int
    actual: int

    def __str__(self) -> str:
        return (
            f"QUOTA  {self.expression!r}: fires {self.actual} times "
            f"in {self.window_hours}h window (limit {self.limit})"
        )


@dataclass
class QuotaResult:
    expression: str
    window_hours: int
    limit: int
    actual: int
    warnings: List[QuotaWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return (
                f"OK     {self.expression!r}: fires {self.actual} times "
                f"in {self.window_hours}h window (limit {self.limit})"
            )
        return "\n".join(str(w) for w in self.warnings)


def check_quota(
    expression: str,
    limit: int = 60,
    window_hours: int = 24,
    reference: datetime | None = None,
) -> QuotaResult:
    """Return a QuotaResult indicating whether *expression* exceeds *limit*
    firings within *window_hours* hours starting from *reference*."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    start = reference or datetime(2024, 1, 1, 0, 0)
    end = start + timedelta(hours=window_hours)
    # Request enough candidates to cover the window; cap at a safe upper bound.
    candidates = next_runs(expression, n=max(limit * 2, 1500), reference=start)
    actual = sum(1 for dt in candidates if dt < end)

    warnings: List[QuotaWarning] = []
    if actual > limit:
        warnings.append(
            QuotaWarning(
                expression=expression,
                window_hours=window_hours,
                limit=limit,
                actual=actual,
            )
        )

    return QuotaResult(
        expression=expression,
        window_hours=window_hours,
        limit=limit,
        actual=actual,
        warnings=warnings,
    )
