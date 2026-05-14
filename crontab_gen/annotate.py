"""Annotation support: attach freeform notes to cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "annotations.json"


@dataclass
class AnnotationEntry:
    expression: str
    note: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "expression": self.expression,
            "note": self.note,
            "created_at": self.created_at,
        }
        if self.updated_at is not None:
            d["updated_at"] = self.updated_at
        return d

    @staticmethod
    def from_dict(data: dict) -> "AnnotationEntry":
        return AnnotationEntry(
            expression=data["expression"],
            note=data["note"],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
        )


def _load(path: Path) -> List[AnnotationEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [AnnotationEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[AnnotationEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_annotation(expression: str, note: str, path: Path = _DEFAULT_PATH) -> AnnotationEntry:
    entries = _load(path)
    now = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        if entry.expression == expression:
            entry.note = note
            entry.updated_at = now
            _save(entries, path)
            return entry
    new_entry = AnnotationEntry(expression=expression, note=note)
    entries.append(new_entry)
    _save(entries, path)
    return new_entry


def get_annotation(expression: str, path: Path = _DEFAULT_PATH) -> Optional[AnnotationEntry]:
    for entry in _load(path):
        if entry.expression == expression:
            return entry
    return None


def remove_annotation(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    filtered = [e for e in entries if e.expression != expression]
    if len(filtered) == len(entries):
        return False
    _save(filtered, path)
    return True


def list_annotations(path: Path = _DEFAULT_PATH) -> List[AnnotationEntry]:
    return _load(path)
