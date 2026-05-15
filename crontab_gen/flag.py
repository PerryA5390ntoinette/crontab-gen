"""Flag module: mark cron expressions with status flags (e.g. active, disabled, review)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_gen", "flags.json")

VALID_FLAGS = {"active", "disabled", "review", "deprecated", "experimental"}


@dataclass
class FlagEntry:
    expression: str
    flag: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    label: Optional[str] = None

    def to_dict(self) -> Dict:
        d = {
            "expression": self.expression,
            "flag": self.flag,
            "created_at": self.created_at,
        }
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(data: Dict) -> "FlagEntry":
        return FlagEntry(
            expression=data["expression"],
            flag=data["flag"],
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            label=data.get("label"),
        )


def _load(path: str) -> List[FlagEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [FlagEntry.from_dict(item) for item in raw]


def _save(entries: List[FlagEntry], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_flag(expression: str, flag: str, label: Optional[str] = None, path: str = _DEFAULT_PATH) -> FlagEntry:
    if flag not in VALID_FLAGS:
        raise ValueError(f"Invalid flag '{flag}'. Must be one of: {sorted(VALID_FLAGS)}")
    entries = _load(path)
    # Remove existing flag for the same expression
    entries = [e for e in entries if e.expression != expression]
    entry = FlagEntry(expression=expression, flag=flag, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_flag(expression: str, path: str = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.expression != expression]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def list_flags(path: str = _DEFAULT_PATH) -> List[FlagEntry]:
    return _load(path)


def get_flag(expression: str, path: str = _DEFAULT_PATH) -> Optional[FlagEntry]:
    for entry in _load(path):
        if entry.expression == expression:
            return entry
    return None
