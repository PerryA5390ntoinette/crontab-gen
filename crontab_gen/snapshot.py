"""Snapshot module: save and compare cron expression snapshots over time."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_gen_snapshots.json")


@dataclass
class SnapshotEntry:
    expression: str
    label: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d = {"expression": self.expression, "created_at": self.created_at}
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(d: dict) -> "SnapshotEntry":
        return SnapshotEntry(
            expression=d["expression"],
            label=d.get("label"),
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


def _load(path: str) -> List[SnapshotEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return [SnapshotEntry.from_dict(item) for item in data]


def _save(entries: List[SnapshotEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_snapshot(expression: str, label: Optional[str] = None, path: str = DEFAULT_PATH) -> SnapshotEntry:
    entries = _load(path)
    entry = SnapshotEntry(expression=expression, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def list_snapshots(path: str = DEFAULT_PATH) -> List[SnapshotEntry]:
    return _load(path)


def clear_snapshots(path: str = DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
