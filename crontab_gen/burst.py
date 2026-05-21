"""Burst detection: identify expressions that fire many times in a short window."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class BurstWarning:
    expression: str
    count: int
    window_minutes: int
    threshold: int

    def __str__(self) -> str:
        return (
            f"BURST  {self.expression!r}  fires {self.count}x "
            f"in {self.window_minutes} min (threshold={self.threshold})"
        )


@dataclass
class BurstResult:
    expression: str
    count: int
    window_minutes: int
    threshold: int
    warnings: List[BurstWarning]

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return (
                f"OK     {self.expression!r}  fires {self.count}x "
                f"in {self.window_minutes} min (threshold={self.threshold})"
            )
        return "\n".join(str(w) for w in self.warnings)


def detect_burst(
    expression: str,
    window_minutes: int = 60,
    threshold: int = 10,
) -> BurstResult:
    """Return a BurstResult for *expression* over *window_minutes* minutes.

    Raises ValueError if the expression is invalid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    # Sample enough runs to cover the window; cap at threshold + 1 to be efficient.
    sample = next_runs(expression, n=threshold + 1)
    if not sample:
        return BurstResult(
            expression=expression,
            count=0,
            window_minutes=window_minutes,
            threshold=threshold,
            warnings=[],
        )

    base = sample[0]
    count = sum(
        1
        for dt in sample
        if (dt - base).total_seconds() <= window_minutes * 60
    )

    warnings: List[BurstWarning] = []
    if count > threshold:
        warnings.append(
            BurstWarning(
                expression=expression,
                count=count,
                window_minutes=window_minutes,
                threshold=threshold,
            )
        )

    return BurstResult(
        expression=expression,
        count=count,
        window_minutes=window_minutes,
        threshold=threshold,
        warnings=warnings,
    )
