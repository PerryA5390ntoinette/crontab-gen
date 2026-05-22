"""Forecast: summarise upcoming fire times for a cron expression over a horizon."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class ForecastResult:
    expression: str
    horizon_hours: int
    fires: List[datetime] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    @property
    def count(self) -> int:
        return len(self.fires)

    @property
    def first(self) -> datetime | None:
        return self.fires[0] if self.fires else None

    @property
    def last(self) -> datetime | None:
        return self.fires[-1] if self.fires else None

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Horizon    : {self.horizon_hours}h",
            f"Fire count : {self.count}",
        ]
        if self.first:
            lines.append(f"First fire : {self.first.strftime('%Y-%m-%d %H:%M')}")
        if self.last and self.last != self.first:
            lines.append(f"Last fire  : {self.last.strftime('%Y-%m-%d %H:%M')}")
        if self.fires:
            lines.append("Next fires :")
            for dt in self.fires[:5]:
                lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
            if self.count > 5:
                lines.append(f"  ... and {self.count - 5} more")
        return "\n".join(lines)


def build_forecast(
    expression: str,
    horizon_hours: int = 24,
    from_dt: datetime | None = None,
) -> ForecastResult:
    """Return a ForecastResult for *expression* over *horizon_hours* hours."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")
    if horizon_hours < 1:
        raise ValueError("horizon_hours must be >= 1")

    start = from_dt or datetime.now().replace(second=0, microsecond=0)
    # Estimate an upper bound: at most once per minute => 60 * horizon_hours
    max_count = 60 * horizon_hours
    candidates = next_runs(expression, max_count, start)

    from datetime import timedelta
    deadline = start + timedelta(hours=horizon_hours)
    fires = [dt for dt in candidates if dt < deadline]

    return ForecastResult(
        expression=expression,
        horizon_hours=horizon_hours,
        fires=fires,
    )
