"""Drift detection: compare scheduled vs actual run times to surface timing drift."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .expression import is_valid
from .next_run import next_runs


@dataclass
class DriftEntry:
    expression: str
    scheduled: datetime
    actual: datetime

    @property
    def delta_seconds(self) -> float:
        return (self.actual - self.scheduled).total_seconds()

    @property
    def abs_delta_seconds(self) -> float:
        return abs(self.delta_seconds)

    def __str__(self) -> str:
        direction = "late" if self.delta_seconds > 0 else "early"
        return (
            f"{self.expression}: scheduled={self.scheduled.strftime('%Y-%m-%d %H:%M')}, "
            f"actual={self.actual.strftime('%Y-%m-%d %H:%M')}, "
            f"drift={self.abs_delta_seconds:.0f}s {direction}"
        )


@dataclass
class DriftReport:
    expression: str
    entries: List[DriftEntry] = field(default_factory=list)
    threshold_seconds: float = 60.0

    @property
    def ok(self) -> bool:
        return all(e.abs_delta_seconds <= self.threshold_seconds for e in self.entries)

    @property
    def max_drift(self) -> Optional[DriftEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.abs_delta_seconds)

    @property
    def avg_drift_seconds(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.delta_seconds for e in self.entries) / len(self.entries)

    def __str__(self) -> str:
        status = "OK" if self.ok else "DRIFT DETECTED"
        lines = [f"Drift report for '{self.expression}' [{status}]"]
        lines.append(f"  Entries   : {len(self.entries)}")
        lines.append(f"  Threshold : {self.threshold_seconds:.0f}s")
        lines.append(f"  Avg drift : {self.avg_drift_seconds:+.1f}s")
        if self.max_drift:
            lines.append(f"  Max drift : {self.max_drift.abs_delta_seconds:.0f}s")
        return "\n".join(lines)


def analyse_drift(
    expression: str,
    actual_times: List[datetime],
    threshold_seconds: float = 60.0,
    reference: Optional[datetime] = None,
) -> DriftReport:
    """Compare a list of actual run datetimes against the nearest scheduled times."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    start = reference or (min(actual_times) - timedelta(hours=1) if actual_times else datetime.now())
    scheduled = next_runs(expression, count=len(actual_times) + 10, start=start)

    entries: List[DriftEntry] = []
    for actual in sorted(actual_times):
        if not scheduled:
            break
        closest = min(scheduled, key=lambda s: abs((s - actual).total_seconds()))
        entries.append(DriftEntry(expression=expression, scheduled=closest, actual=actual))
        scheduled = [s for s in scheduled if s != closest]

    return DriftReport(expression=expression, entries=entries, threshold_seconds=threshold_seconds)
