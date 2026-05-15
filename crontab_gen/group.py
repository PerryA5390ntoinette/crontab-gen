"""Group multiple cron expressions under a named collection."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "groups.json"


@dataclass
class GroupEntry:
    name: str
    expressions: List[str]
    description: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "expressions": self.expressions,
            "created_at": self.created_at,
        }
        if self.description is not None:
            d["description"] = self.description
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "GroupEntry":
        return cls(
            name=data["name"],
            expressions=data["expressions"],
            description=data.get("description"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


def _load(path: Path) -> List[GroupEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [GroupEntry.from_dict(d) for d in json.load(fh)]


def _save(entries: List[GroupEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_group(name: str, expressions: List[str], description: Optional[str] = None,
              path: Path = _DEFAULT_PATH) -> GroupEntry:
    entries = _load(path)
    entry = GroupEntry(name=name, expressions=expressions, description=description)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_group(name: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.name != name]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def list_groups(path: Path = _DEFAULT_PATH) -> List[GroupEntry]:
    return _load(path)


def get_group(name: str, path: Path = _DEFAULT_PATH) -> Optional[GroupEntry]:
    return next((e for e in _load(path) if e.name == name), None)
