"""Symmetry analysis: detect whether two cron expressions fire at mirrored
times within a 24-hour period (e.g. 06:00 and 18:00)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class SymmetryResult:
    expression_a: str
    expression_b: str
    mirrored_pairs: List[tuple] = field(default_factory=list)
    score: float = 0.0  # 0.0 – 1.0; 1.0 means perfectly mirrored

    @property
    def is_symmetric(self) -> bool:
        return self.score >= 0.5

    def __str__(self) -> str:
        lines = [
            f"Symmetry analysis: '{self.expression_a}'  vs  '{self.expression_b}'",
            f"  Score       : {self.score:.2f}  ({'symmetric' if self.is_symmetric else 'asymmetric'})",
            f"  Paired fires: {len(self.mirrored_pairs)}",
        ]
        for a_time, b_time in self.mirrored_pairs[:5]:
            lines.append(f"    {a_time.strftime('%H:%M')}  <->  {b_time.strftime('%H:%M')}")
        if len(self.mirrored_pairs) > 5:
            lines.append(f"    … and {len(self.mirrored_pairs) - 5} more")
        return "\n".join(lines)


def _times_in_minutes(expression: str, horizon_hours: int) -> List[int]:
    """Return fire times as minutes-since-midnight for the first *horizon_hours*."""
    runs = next_runs(expression, count=horizon_hours * 60)
    result: List[int] = []
    seen_days: set = set()
    for dt in runs:
        day = dt.date()
        if day not in seen_days:
            if len(seen_days) >= horizon_hours // 24 + 1:
                break
            seen_days.add(day)
        result.append(dt.hour * 60 + dt.minute)
    return result


def analyse_symmetry(
    expression_a: str,
    expression_b: str,
    horizon_hours: int = 24,
    tolerance_minutes: int = 0,
) -> SymmetryResult:
    """Compare two expressions and measure how symmetrically they fire.

    A pair of fire times is considered *mirrored* when their minutes-since-midnight
    sum to 1440 (i.e. they are equidistant from midnight / noon).
    """
    if not is_valid(expression_a):
        raise ValueError(f"Invalid cron expression: {expression_a!r}")
    if not is_valid(expression_b):
        raise ValueError(f"Invalid cron expression: {expression_b!r}")

    runs_a = next_runs(expression_a, count=horizon_hours * 60)
    runs_b = next_runs(expression_b, count=horizon_hours * 60)

    minutes_a = sorted({r.hour * 60 + r.minute for r in runs_a})
    minutes_b = sorted({r.hour * 60 + r.minute for r in runs_b})

    paired: List[tuple] = []
    used_b: set = set()

    for ma in minutes_a:
        mirror = 1440 - ma
        for mb in minutes_b:
            if mb in used_b:
                continue
            if abs(mb - mirror) <= tolerance_minutes:
                # find actual datetime objects for display
                dt_a = next((r for r in runs_a if r.hour * 60 + r.minute == ma), None)
                dt_b = next((r for r in runs_b if r.hour * 60 + r.minute == mb), None)
                if dt_a and dt_b:
                    paired.append((dt_a, dt_b))
                used_b.add(mb)
                break

    total = max(len(minutes_a), len(minutes_b), 1)
    score = len(paired) / total

    return SymmetryResult(
        expression_a=expression_a,
        expression_b=expression_b,
        mirrored_pairs=paired,
        score=round(score, 4),
    )
