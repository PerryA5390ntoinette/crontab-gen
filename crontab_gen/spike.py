"""Detect expression spikes: unusual bursts relative to a rolling baseline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .next_run import next_runs
from .expression import is_valid


@dataclass
class SpikeWarning:
    expression: str
    window_minutes: int
    count: int
    threshold: int

    def __str__(self) -> str:
        return (
            f"SPIKE  {self.expression!r}  "
            f"{self.count} fires in {self.window_minutes}-min window "
            f"(threshold={self.threshold})"
        )


@dataclass
class SpikeResult:
    expression: str
    window_minutes: int
    threshold: int
    fires: int
    warnings: List[SpikeWarning] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok():
            return (
                f"OK  {self.expression!r}  "
                f"{self.fires} fires in {self.window_minutes}-min window "
                f"(threshold={self.threshold})"
            )
        lines = [f"SPIKE DETECTED  {self.expression!r}"]
        for w in self.warnings:
            lines.append(f"  {w}")
        return "\n".join(lines)


def detect_spike(
    expression: str,
    window_minutes: int = 60,
    threshold: int = 10,
) -> SpikeResult:
    """Count fires within *window_minutes* and warn if count exceeds threshold."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    # Sample enough candidates to cover the window
    candidates = next_runs(expression, count=window_minutes + 10)
    if not candidates:
        return SpikeResult(
            expression=expression,
            window_minutes=window_minutes,
            threshold=threshold,
            fires=0,
        )

    origin = candidates[0]
    from datetime import timedelta

    cutoff = origin + timedelta(minutes=window_minutes)
    fires = sum(1 for dt in candidates if dt <= cutoff)

    warnings: List[SpikeWarning] = []
    if fires > threshold:
        warnings.append(
            SpikeWarning(
                expression=expression,
                window_minutes=window_minutes,
                count=fires,
                threshold=threshold,
            )
        )

    return SpikeResult(
        expression=expression,
        window_minutes=window_minutes,
        threshold=threshold,
        fires=fires,
        warnings=warnings,
    )
