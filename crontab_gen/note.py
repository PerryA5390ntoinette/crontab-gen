"""Persistent notes attached to cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "notes.json"


@dataclass
class NoteEntry:
    expression: str
    text: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "expression": self.expression,
            "text": self.text,
            "created_at": self.created_at,
        }
        if self.updated_at is not None:
            d["updated_at"] = self.updated_at
        return d

    @staticmethod
    def from_dict(data: dict) -> "NoteEntry":
        return NoteEntry(
            expression=data["expression"],
            text=data["text"],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
        )


def _load(path: Path) -> List[NoteEntry]:
    if not path.exists():
        return []
    with open(path) as fh:
        return [NoteEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[NoteEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_note(expression: str, text: str, path: Path = _DEFAULT_PATH) -> NoteEntry:
    entries = _load(path)
    entry = NoteEntry(expression=expression, text=text)
    entries.append(entry)
    _save(entries, path)
    return entry


def list_notes(expression: Optional[str] = None, path: Path = _DEFAULT_PATH) -> List[NoteEntry]:
    entries = _load(path)
    if expression is not None:
        entries = [e for e in entries if e.expression == expression]
    return entries


def remove_note(expression: str, index: int, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    targets = [e for e in entries if e.expression == expression]
    if index < 0 or index >= len(targets):
        return False
    entries.remove(targets[index])
    _save(entries, path)
    return True


def update_note(expression: str, index: int, text: str, path: Path = _DEFAULT_PATH) -> Optional[NoteEntry]:
    entries = _load(path)
    targets = [(i, e) for i, e in enumerate(entries) if e.expression == expression]
    if index < 0 or index >= len(targets):
        return None
    global_idx, entry = targets[index]
    entry.text = text
    entry.updated_at = datetime.now(timezone.utc).isoformat()
    entries[global_idx] = entry
    _save(entries, path)
    return entry
