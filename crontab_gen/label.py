"""Label management for cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_gen_labels.json")


@dataclass
class LabelEntry:
    expression: str
    label: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: Dict) -> "LabelEntry":
        return LabelEntry(
            expression=data["expression"],
            label=data["label"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )


def _load(path: str) -> List[LabelEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [LabelEntry.from_dict(d) for d in raw]


def _save(entries: List[LabelEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_label(expression: str, label: str, path: str = _DEFAULT_PATH) -> LabelEntry:
    entries = _load(path)
    entry = LabelEntry(expression=expression, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_label(expression: str, path: str = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.expression != expression]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def list_labels(path: str = _DEFAULT_PATH) -> List[LabelEntry]:
    return _load(path)


def find_label(expression: str, path: str = _DEFAULT_PATH) -> Optional[LabelEntry]:
    for entry in _load(path):
        if entry.expression == expression:
            return entry
    return None
