"""Time-window analysis: check how many times a cron expression fires within a given hour range."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .expression import is_valid
from .next_run import next_runs
from datetime import datetime, timedelta


@dataclass
class WindowWarning:
    expression: str
    count: int
    start_hour: int
    end_hour: int
    threshold: int

    def __str__(self) -> str:
        return (
            f"Warning: '{self.expression}' fires {self.count} time(s) between "
            f"{self.start_hour:02d}:00 and {self.end_hour:02d}:00 "
            f"(threshold: {self.threshold})"
        )


@dataclass
class WindowResult:
    expression: str
    start_hour: int
    end_hour: int
    count: int
    warnings: List[WindowWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return (
                f"OK: '{self.expression}' fires {self.count} time(s) between "
                f"{self.start_hour:02d}:00 and {self.end_hour:02d}:00"
            )
        return "\n".join(str(w) for w in self.warnings)


def analyse_window(
    expression: str,
    start_hour: int = 9,
    end_hour: int = 17,
    threshold: int = 20,
    horizon_days: int = 1,
) -> WindowResult:
    """Count how many times *expression* fires within [start_hour, end_hour) on the
    next *horizon_days* days and warn if the count exceeds *threshold*."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")
    if not (0 <= start_hour < end_hour <= 24):
        raise ValueError("start_hour must be < end_hour and both in [0, 24]")

    # Collect a generous sample of upcoming runs and filter to the window.
    sample_size = horizon_days * 24 * 60  # upper bound: every minute
    candidates = next_runs(expression, n=sample_size)

    cutoff = datetime.now() + timedelta(days=horizon_days)
    in_window = [
        dt
        for dt in candidates
        if dt <= cutoff and start_hour <= dt.hour < end_hour
    ]
    count = len(in_window)

    warnings: List[WindowWarning] = []
    if count > threshold:
        warnings.append(
            WindowWarning(
                expression=expression,
                count=count,
                start_hour=start_hour,
                end_hour=end_hour,
                threshold=threshold,
            )
        )

    return WindowResult(
        expression=expression,
        start_hour=start_hour,
        end_hour=end_hour,
        count=count,
        warnings=warnings,
    )
