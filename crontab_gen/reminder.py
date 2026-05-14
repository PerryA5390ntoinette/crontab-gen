"""Reminder annotations attached to cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DEFAULT_PATH = Path.home() / ".crontab_gen" / "reminders.json"


@dataclass
class ReminderEntry:
    expression: str
    message: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    label: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "expression": self.expression,
            "message": self.message,
            "created_at": self.created_at,
        }
        if self.label is not None:
            d["label"] = self.label
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ReminderEntry":
        return cls(
            expression=data["expression"],
            message=data["message"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            label=data.get("label"),
        )


def _load(path: Path) -> List[ReminderEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [ReminderEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[ReminderEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_reminder(
    expression: str,
    message: str,
    label: Optional[str] = None,
    path: Path = DEFAULT_PATH,
) -> ReminderEntry:
    entries = _load(path)
    entry = ReminderEntry(expression=expression, message=message, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def list_reminders(path: Path = DEFAULT_PATH) -> List[ReminderEntry]:
    return _load(path)


def clear_reminders(path: Path = DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
