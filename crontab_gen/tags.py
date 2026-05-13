"""Tag management for labeling and organizing cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os

_DEFAULT_TAGS_FILE = os.path.join(
    os.path.expanduser("~"), ".crontab_gen", "tags.json"
)


@dataclass
class TagEntry:
    expression: str
    tags: List[str] = field(default_factory=list)
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {"expression": self.expression, "tags": self.tags, "note": self.note}

    @staticmethod
    def from_dict(data: dict) -> "TagEntry":
        return TagEntry(
            expression=data["expression"],
            tags=data.get("tags", []),
            note=data.get("note"),
        )


def _load(path: str = _DEFAULT_TAGS_FILE) -> Dict[str, TagEntry]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        raw = json.load(fh)
    return {k: TagEntry.from_dict(v) for k, v in raw.items()}


def _save(entries: Dict[str, TagEntry], path: str = _DEFAULT_TAGS_FILE) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump({k: v.to_dict() for k, v in entries.items()}, fh, indent=2)


def add_tag(
    expression: str,
    tags: List[str],
    note: Optional[str] = None,
    path: str = _DEFAULT_TAGS_FILE,
) -> TagEntry:
    entries = _load(path)
    entry = entries.get(expression, TagEntry(expression=expression))
    for tag in tags:
        if tag not in entry.tags:
            entry.tags.append(tag)
    if note is not None:
        entry.note = note
    entries[expression] = entry
    _save(entries, path)
    return entry


def remove_tag(
    expression: str, tags: List[str], path: str = _DEFAULT_TAGS_FILE
) -> Optional[TagEntry]:
    entries = _load(path)
    entry = entries.get(expression)
    if entry is None:
        return None
    entry.tags = [t for t in entry.tags if t not in tags]
    entries[expression] = entry
    _save(entries, path)
    return entry


def find_by_tag(tag: str, path: str = _DEFAULT_TAGS_FILE) -> List[TagEntry]:
    entries = _load(path)
    return [e for e in entries.values() if tag in e.tags]


def list_tags(path: str = _DEFAULT_TAGS_FILE) -> List[TagEntry]:
    return list(_load(path).values())
