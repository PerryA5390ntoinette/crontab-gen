"""Pin module: pin frequently used cron expressions for quick access."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "pins.json"


@dataclass
class PinEntry:
    expression: str
    label: Optional[str] = None
    pinned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d: dict = {"expression": self.expression, "pinned_at": self.pinned_at}
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(data: dict) -> "PinEntry":
        return PinEntry(
            expression=data["expression"],
            label=data.get("label"),
            pinned_at=data.get("pinned_at", datetime.now(timezone.utc).isoformat()),
        )


def _load(path: Path) -> List[PinEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        raw = json.load(fh)
    return [PinEntry.from_dict(r) for r in raw]


def _save(entries: List[PinEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_pin(expression: str, label: Optional[str] = None, path: Path = _DEFAULT_PATH) -> PinEntry:
    entries = _load(path)
    entry = PinEntry(expression=expression, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def remove_pin(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new_entries = [e for e in entries if e.expression != expression]
    if len(new_entries) == len(entries):
        return False
    _save(new_entries, path)
    return True


def list_pins(path: Path = _DEFAULT_PATH) -> List[PinEntry]:
    return _load(path)


def clear_pins(path: Path = _DEFAULT_PATH) -> int:
    entries = _load(path)
    count = len(entries)
    _save([], path)
    return count
