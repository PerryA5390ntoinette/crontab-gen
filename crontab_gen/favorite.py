"""Persistent favorites store for cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "favorites.json"


@dataclass
class FavoriteEntry:
    expression: str
    label: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d: dict = {
            "expression": self.expression,
            "created_at": self.created_at,
        }
        if self.label is not None:
            d["label"] = self.label
        if self.tags:
            d["tags"] = self.tags
        return d

    @staticmethod
    def from_dict(data: dict) -> "FavoriteEntry":
        return FavoriteEntry(
            expression=data["expression"],
            label=data.get("label"),
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


def _load(path: Path) -> List[FavoriteEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        raw = json.load(fh)
    return [FavoriteEntry.from_dict(r) for r in raw]


def _save(entries: List[FavoriteEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_favorite(expression: str, label: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 path: Path = _DEFAULT_PATH) -> FavoriteEntry:
    entries = _load(path)
    entry = FavoriteEntry(expression=expression, label=label, tags=tags or [])
    entries.append(entry)
    _save(entries, path)
    return entry


def list_favorites(path: Path = _DEFAULT_PATH) -> List[FavoriteEntry]:
    return _load(path)


def remove_favorite(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    before = len(entries)
    entries = [e for e in entries if e.expression != expression]
    if len(entries) == before:
        return False
    _save(entries, path)
    return True


def clear_favorites(path: Path = _DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
