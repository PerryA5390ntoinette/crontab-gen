"""Watchlist: persist cron expressions the user wants to monitor."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "watchlist.json"


@dataclass
class WatchEntry:
    expression: str
    label: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        d: dict = {"expression": self.expression, "created_at": self.created_at}
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(data: dict) -> "WatchEntry":
        return WatchEntry(
            expression=data["expression"],
            label=data.get("label"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


def _load(path: Path) -> List[WatchEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        raw = json.load(fh)
    return [WatchEntry.from_dict(item) for item in raw]


def _save(entries: List[WatchEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_entry(
    expression: str,
    label: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> WatchEntry:
    entries = _load(path)
    entry = WatchEntry(expression=expression, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def list_entries(path: Path = _DEFAULT_PATH) -> List[WatchEntry]:
    return _load(path)


def remove_entry(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.expression != expression]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def clear_entries(path: Path = _DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
