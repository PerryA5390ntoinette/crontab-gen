"""Detect idle periods — time gaps between consecutive cron fires."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class IdleGap:
    """A gap between two consecutive cron fires."""

    start: str
    end: str
    gap_minutes: int

    def __str__(self) -> str:
        return (
            f"Idle {self.gap_minutes}m between {self.start} and {self.end}"
        )


@dataclass
class IdleResult:
    """Result of idle-gap analysis for a cron expression."""

    expression: str
    gaps: List[IdleGap] = field(default_factory=list)
    threshold_minutes: int = 60

    @property
    def max_gap(self) -> int:
        """Return the longest idle gap in minutes, or 0 if no gaps."""
        return max((g.gap_minutes for g in self.gaps), default=0)

    @property
    def long_gaps(self) -> List[IdleGap]:
        """Return gaps that exceed the threshold."""
        return [g for g in self.gaps if g.gap_minutes >= self.threshold_minutes]

    @property
    def has_long_gaps(self) -> bool:
        return bool(self.long_gaps)

    def __str__(self) -> str:
        lines = [f"Idle analysis for '{self.expression}' (threshold={self.threshold_minutes}m)"]
        if not self.gaps:
            lines.append("  No gaps detected.")
        else:
            lines.append(f"  Max gap : {self.max_gap}m")
            lines.append(f"  Long gaps: {len(self.long_gaps)}")
            for g in self.long_gaps:
                lines.append(f"    {g}")
        return "\n".join(lines)


def analyse_idle(
    expression: str,
    horizon_hours: int = 24,
    threshold_minutes: int = 60,
) -> IdleResult:
    """Analyse idle gaps for *expression* over the next *horizon_hours* hours.

    Raises ValueError if the expression is invalid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    # Request enough samples to cover the horizon.
    sample_count = max(horizon_hours * 60, 120)
    fires = next_runs(expression, count=sample_count)

    gaps: list[IdleGap] = []
    for a, b in zip(fires, fires[1:]):
        diff = int((b - a).total_seconds() // 60)
        gaps.append(
            IdleGap(
                start=a.strftime("%Y-%m-%d %H:%M"),
                end=b.strftime("%Y-%m-%d %H:%M"),
                gap_minutes=diff,
            )
        )

    return IdleResult(
        expression=expression,
        gaps=gaps,
        threshold_minutes=threshold_minutes,
    )
