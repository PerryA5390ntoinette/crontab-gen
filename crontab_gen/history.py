"""Session history for recently used/built cron expressions."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = Path.home() / ".crontab_gen_history.json"
MAX_HISTORY = 50


@dataclass
class HistoryEntry:
    expression: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            expression=data["expression"],
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
        )


def _load(path: Path) -> List[HistoryEntry]:
    if not path.exists():
        return []
    try:
        with path.open() as fh:
            raw = json.load(fh)
        return [HistoryEntry.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError):
        return []


def _save(entries: List[HistoryEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_entry(
    expression: str,
    description: str,
    path: Path = DEFAULT_HISTORY_FILE,
) -> HistoryEntry:
    """Append a new entry, keeping at most MAX_HISTORY entries."""
    entries = _load(path)
    entry = HistoryEntry(expression=expression, description=description)
    entries.insert(0, entry)
    _save(entries[:MAX_HISTORY], path)
    return entry


def get_history(
    limit: Optional[int] = None,
    path: Path = DEFAULT_HISTORY_FILE,
) -> List[HistoryEntry]:
    """Return history entries, newest first."""
    entries = _load(path)
    return entries[:limit] if limit is not None else entries


def clear_history(path: Path = DEFAULT_HISTORY_FILE) -> int:
    """Delete all history entries. Returns number of entries removed."""
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
