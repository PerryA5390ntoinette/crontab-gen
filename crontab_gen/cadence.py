"""Cadence analysis: classify how frequently a cron expression fires."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .expression import is_valid
from .next_run import next_runs


_LABELS = [
    (1, "every minute"),
    (5, "every few minutes"),
    (15, "sub-hourly"),
    (60, "hourly"),
    (360, "several times a day"),
    (1440, "daily"),
    (10080, "weekly"),
    (43200, "monthly"),
]


@dataclass
class CadenceResult:
    expression: str
    avg_gap_minutes: float
    label: str
    fires_per_day: float

    def __str__(self) -> str:
        return (
            f"{self.expression!r}: {self.label} "
            f"(~{self.fires_per_day:.1f}x/day, avg gap {self.avg_gap_minutes:.1f} min)"
        )


def _classify(avg_gap: float) -> str:
    for threshold, label in _LABELS:
        if avg_gap <= threshold:
            return label
    return "infrequent"


def analyse_cadence(expression: str, sample: int = 10) -> CadenceResult:
    """Return a CadenceResult describing how often *expression* fires.

    Raises ValueError if the expression is invalid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    runs = next_runs(expression, count=sample + 1)
    if len(runs) < 2:
        raise ValueError("Could not compute enough future runs to analyse cadence.")

    gaps = [
        (runs[i + 1] - runs[i]).total_seconds() / 60
        for i in range(len(runs) - 1)
    ]
    avg_gap = sum(gaps) / len(gaps)
    fires_per_day = 1440.0 / avg_gap if avg_gap > 0 else 0.0
    label = _classify(avg_gap)
    return CadenceResult(
        expression=expression,
        avg_gap_minutes=round(avg_gap, 2),
        label=label,
        fires_per_day=round(fires_per_day, 2),
    )
