"""Bookmark management for saving favourite cron expressions with labels."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_gen", "bookmarks.json")


@dataclass
class BookmarkEntry:
    expression: str
    label: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "BookmarkEntry":
        return BookmarkEntry(
            expression=data["expression"],
            label=data["label"],
            created_at=data.get("created_at", ""),
        )


def _load(path: str = DEFAULT_PATH) -> List[BookmarkEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [BookmarkEntry.from_dict(d) for d in raw]


def _save(entries: List[BookmarkEntry], path: str = DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_bookmark(expression: str, label: str, path: str = DEFAULT_PATH) -> BookmarkEntry:
    entries = _load(path)
    entry = BookmarkEntry(expression=expression, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_bookmark(label: str, path: str = DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.label != label]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def list_bookmarks(path: str = DEFAULT_PATH) -> List[BookmarkEntry]:
    return _load(path)


def find_bookmark(label: str, path: str = DEFAULT_PATH) -> Optional[BookmarkEntry]:
    for entry in _load(path):
        if entry.label == label:
            return entry
    return None
