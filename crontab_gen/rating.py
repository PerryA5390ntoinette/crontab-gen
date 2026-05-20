"""User ratings for cron expressions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "ratings.json"


@dataclass
class RatingEntry:
    expression: str
    score: int  # 1-5
    label: Optional[str] = None

    def to_dict(self) -> Dict:
        d: Dict = {"expression": self.expression, "score": self.score}
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(d: Dict) -> "RatingEntry":
        return RatingEntry(
            expression=d["expression"],
            score=int(d["score"]),
            label=d.get("label"),
        )


def _load(path: Path) -> List[RatingEntry]:
    if not path.exists():
        return []
    with path.open() as fh:
        data = json.load(fh)
    return [RatingEntry.from_dict(item) for item in data]


def _save(entries: List[RatingEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def add_rating(
    expression: str,
    score: int,
    label: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> RatingEntry:
    if score < 1 or score > 5:
        raise ValueError(f"Score must be between 1 and 5, got {score}")
    entries = _load(path)
    # Replace existing rating for same expression
    entries = [e for e in entries if e.expression != expression]
    entry = RatingEntry(expression=expression, score=score, label=label)
    entries.append(entry)
    _save(entries, path)
    return entry


def get_rating(expression: str, path: Path = _DEFAULT_PATH) -> Optional[RatingEntry]:
    for entry in _load(path):
        if entry.expression == expression:
            return entry
    return None


def list_ratings(path: Path = _DEFAULT_PATH) -> List[RatingEntry]:
    return _load(path)


def remove_rating(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    filtered = [e for e in entries if e.expression != expression]
    if len(filtered) == len(entries):
        return False
    _save(filtered, path)
    return True
