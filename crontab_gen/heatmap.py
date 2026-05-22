"""Heatmap: visualise cron expression firing density across a 24-hour day."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_gen.expression import is_valid
from crontab_gen.next_run import next_runs

_HOURS = 24
_BLOCK_FULL = "█"
_BLOCK_EMPTY = "░"


@dataclass
class HeatmapResult:
    expression: str
    # fires_per_hour[h] = number of fires in hour h (0-23)
    fires_per_hour: List[int] = field(default_factory=lambda: [0] * _HOURS)

    @property
    def peak_hour(self) -> int:
        return self.fires_per_hour.index(max(self.fires_per_hour))

    @property
    def total_fires(self) -> int:
        return sum(self.fires_per_hour)

    def __str__(self) -> str:
        max_fires = max(self.fires_per_hour) or 1
        rows = [f"Heatmap for: {self.expression}"]
        for h in range(_HOURS):
            count = self.fires_per_hour[h]
            bar_len = round((count / max_fires) * 20)
            bar = _BLOCK_FULL * bar_len + _BLOCK_EMPTY * (20 - bar_len)
            rows.append(f"  {h:02d}:00  {bar}  ({count})")
        rows.append(f"  Peak hour: {self.peak_hour:02d}:00  |  Total fires: {self.total_fires}")
        return "\n".join(rows)


def build_heatmap(expression: str, days: int = 7) -> HeatmapResult:
    """Return a HeatmapResult counting fires per hour over *days* days."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    count = days * _HOURS * 60  # upper bound on samples needed
    runs = next_runs(expression, count=count, horizon_days=days)

    fires_per_hour = [0] * _HOURS
    for dt in runs:
        fires_per_hour[dt.hour] += 1

    result = HeatmapResult(expression=expression, fires_per_hour=fires_per_hour)
    return result
