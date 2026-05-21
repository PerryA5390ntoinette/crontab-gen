"""Track consecutive-day usage streaks for cron expressions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "streaks.json"


@dataclass
class StreakEntry:
    expression: str
    dates: List[str] = field(default_factory=list)  # ISO date strings

    def to_dict(self) -> dict:
        return {"expression": self.expression, "dates": self.dates}

    @staticmethod
    def from_dict(data: dict) -> "StreakEntry":
        return StreakEntry(
            expression=data["expression"],
            dates=data.get("dates", []),
        )

    def record_today(self) -> None:
        today = date.today().isoformat()
        if today not in self.dates:
            self.dates.append(today)
            self.dates.sort()

    @property
    def current_streak(self) -> int:
        if not self.dates:
            return 0
        sorted_dates = sorted(date.fromisoformat(d) for d in self.dates)
        streak = 1
        for i in range(len(sorted_dates) - 1, 0, -1):
            if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
                streak += 1
            else:
                break
        # streak only counts if the last date is today or yesterday
        last = sorted_dates[-1]
        today = date.today()
        if last < today - timedelta(days=1):
            return 0
        return streak

    @property
    def longest_streak(self) -> int:
        if not self.dates:
            return 0
        sorted_dates = sorted(date.fromisoformat(d) for d in self.dates)
        best = current = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
                current += 1
                best = max(best, current)
            else:
                current = 1
        return best


def _load(path: Path) -> List[StreakEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [StreakEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[StreakEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def record(expression: str, path: Path = _DEFAULT_PATH) -> StreakEntry:
    entries = _load(path)
    for entry in entries:
        if entry.expression == expression:
            entry.record_today()
            _save(entries, path)
            return entry
    entry = StreakEntry(expression=expression)
    entry.record_today()
    entries.append(entry)
    _save(entries, path)
    return entry


def get_streak(expression: str, path: Path = _DEFAULT_PATH) -> Optional[StreakEntry]:
    for entry in _load(path):
        if entry.expression == expression:
            return entry
    return None


def all_streaks(path: Path = _DEFAULT_PATH) -> List[StreakEntry]:
    return _load(path)
