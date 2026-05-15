"""Priority tagging for cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "priorities.json"

LEVELS = ("low", "medium", "high", "critical")


@dataclass
class PriorityEntry:
    expression: str
    level: str
    label: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        d: Dict = {
            "expression": self.expression,
            "level": self.level,
            "created_at": self.created_at,
        }
        if self.label is not None:
            d["label"] = self.label
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> "PriorityEntry":
        return cls(
            expression=data["expression"],
            level=data["level"],
            label=data.get("label"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )


def _load(path: Path) -> List[PriorityEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [PriorityEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[PriorityEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_priority(expression: str, level: str, label: Optional[str] = None,
                 path: Path = _DEFAULT_PATH) -> PriorityEntry:
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}, got {level!r}")
    entries = _load(path)
    entry = PriorityEntry(expression=expression, level=level, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_priority(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new = [e for e in entries if e.expression != expression]
    if len(new) == len(entries):
        return False
    _save(new, path)
    return True


def list_priorities(level: Optional[str] = None,
                    path: Path = _DEFAULT_PATH) -> List[PriorityEntry]:
    entries = _load(path)
    if level:
        entries = [e for e in entries if e.level == level]
    return entries
