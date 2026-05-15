"""Archive module: soft-delete cron expressions by moving them to an archive store."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "archive.json"


@dataclass
class ArchiveEntry:
    expression: str
    label: Optional[str] = None
    archived_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Optional[str] = None  # e.g. 'bookmark', 'favorite', 'tag'

    def to_dict(self) -> dict:
        d: dict = {"expression": self.expression, "archived_at": self.archived_at}
        if self.label is not None:
            d["label"] = self.label
        if self.source is not None:
            d["source"] = self.source
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        return cls(
            expression=data["expression"],
            label=data.get("label"),
            archived_at=data.get("archived_at", datetime.now(timezone.utc).isoformat()),
            source=data.get("source"),
        )


def _load(path: Path) -> List[ArchiveEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        raw = json.load(fh)
    return [ArchiveEntry.from_dict(r) for r in raw]


def _save(entries: List[ArchiveEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def archive_expression(
    expression: str,
    label: Optional[str] = None,
    source: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> ArchiveEntry:
    entries = _load(path)
    entry = ArchiveEntry(expression=expression, label=label, source=source)
    entries.append(entry)
    _save(entries, path)
    return entry


def list_archive(path: Path = _DEFAULT_PATH) -> List[ArchiveEntry]:
    return _load(path)


def clear_archive(path: Path = _DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count


def remove_from_archive(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.expression != expression]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True
