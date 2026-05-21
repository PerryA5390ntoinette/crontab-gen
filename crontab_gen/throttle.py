"""Throttle analysis: detect cron expressions that fire too frequently."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .expression import is_valid
from .next_run import next_runs


# Minimum gap in seconds considered "safe" by default
_DEFAULT_MIN_GAP_SECONDS = 60


@dataclass
class ThrottleWarning:
    expression: str
    min_gap_seconds: float
    threshold_seconds: int

    def __str__(self) -> str:
        return (
            f"Expression '{self.expression}' fires as frequently as every "
            f"{self.min_gap_seconds:.0f}s "
            f"(threshold: {self.threshold_seconds}s)"
        )


@dataclass
class ThrottleResult:
    expression: str
    warnings: List[ThrottleWarning]

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return f"OK: '{self.expression}' is within throttle limits"
        lines = [f"THROTTLE WARNINGS for '{self.expression}':"] + [
            f"  - {w}" for w in self.warnings
        ]
        return "\n".join(lines)


def analyse(
    expression: str,
    threshold_seconds: int = _DEFAULT_MIN_GAP_SECONDS,
    sample_size: int = 10,
) -> ThrottleResult:
    """Analyse an expression and return a ThrottleResult.

    Raises ValueError if the expression is invalid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    runs = next_runs(expression, count=sample_size)
    warnings: List[ThrottleWarning] = []

    if len(runs) >= 2:
        gaps = [
            (runs[i + 1] - runs[i]).total_seconds()
            for i in range(len(runs) - 1)
        ]
        min_gap = min(gaps)
        if min_gap < threshold_seconds:
            warnings.append(
                ThrottleWarning(
                    expression=expression,
                    min_gap_seconds=min_gap,
                    threshold_seconds=threshold_seconds,
                )
            )

    return ThrottleResult(expression=expression, warnings=warnings)
