"""User-defined aliases for cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_gen_aliases.json")


@dataclass
class AliasEntry:
    name: str
    expression: str
    description: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "expression": self.expression, "description": self.description}

    @staticmethod
    def from_dict(d: dict) -> "AliasEntry":
        return AliasEntry(
            name=d["name"],
            expression=d["expression"],
            description=d.get("description", ""),
        )


def _load(path: str) -> List[AliasEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return [AliasEntry.from_dict(e) for e in data]


def _save(entries: List[AliasEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_alias(name: str, expression: str, description: str = "", path: str = DEFAULT_PATH) -> AliasEntry:
    entries = _load(path)
    entries = [e for e in entries if e.name.lower() != name.lower()]
    entry = AliasEntry(name=name, expression=expression, description=description)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_alias(name: str, path: str = DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.name.lower() != name.lower()]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def get_alias(name: str, path: str = DEFAULT_PATH) -> Optional[AliasEntry]:
    for entry in _load(path):
        if entry.name.lower() == name.lower():
            return entry
    return None


def list_aliases(path: str = DEFAULT_PATH) -> List[AliasEntry]:
    return _load(path)
