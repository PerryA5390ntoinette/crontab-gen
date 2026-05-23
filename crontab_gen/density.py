"""Density analysis: measure how many times an expression fires within a
given time window and classify the load as low / medium / high."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .expression import is_valid
from .next_run import next_runs


_LOW_THRESHOLD = 24      # fires per 24 h
_HIGH_THRESHOLD = 120    # fires per 24 h


@dataclass
class DensityResult:
    expression: str
    window_hours: int
    fire_count: int
    label: str          # "low" | "medium" | "high"

    def fires_per_hour(self) -> float:
        if self.window_hours == 0:
            return 0.0
        return self.fire_count / self.window_hours

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Window     : {self.window_hours}h\n"
            f"Fires      : {self.fire_count}\n"
            f"Per hour   : {self.fires_per_hour():.2f}\n"
            f"Density    : {self.label}"
        )


def _classify(fire_count: int, window_hours: int) -> str:
    normalised = fire_count * 24 / max(window_hours, 1)
    if normalised <= _LOW_THRESHOLD:
        return "low"
    if normalised <= _HIGH_THRESHOLD:
        return "medium"
    return "high"


def analyse_density(expression: str, window_hours: int = 24) -> DensityResult:
    """Return a DensityResult for *expression* over *window_hours* hours."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")
    if window_hours <= 0:
        raise ValueError("window_hours must be a positive integer")

    runs: List = next_runs(expression, count=window_hours * 60, hours=window_hours)
    fire_count = len(runs)
    label = _classify(fire_count, window_hours)
    return DensityResult(
        expression=expression,
        window_hours=window_hours,
        fire_count=fire_count,
        label=label,
    )
