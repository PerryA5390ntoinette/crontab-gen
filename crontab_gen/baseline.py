"""Baseline: save and compare a reference cron expression against the current one."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "baseline.json"


@dataclass
class BaselineEntry:
    expression: str
    label: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"expression": self.expression}
        if self.label is not None:
            d["label"] = self.label
        return d

    @staticmethod
    def from_dict(d: dict) -> "BaselineEntry":
        return BaselineEntry(
            expression=d["expression"],
            label=d.get("label"),
        )


@dataclass
class BaselineComparison:
    baseline: str
    current: str
    changed: bool
    baseline_description: str
    current_description: str

    def __str__(self) -> str:
        status = "CHANGED" if self.changed else "UNCHANGED"
        lines = [
            f"Status     : {status}",
            f"Baseline   : {self.baseline}",
            f"             {self.baseline_description}",
            f"Current    : {self.current}",
            f"             {self.current_description}",
        ]
        return "\n".join(lines)


def _load(path: Path) -> Optional[BaselineEntry]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return BaselineEntry.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def _save(entry: BaselineEntry, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry.to_dict(), indent=2))


def set_baseline(
    expression: str,
    label: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> BaselineEntry:
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")
    entry = BaselineEntry(expression=expression, label=label)
    _save(entry, path)
    return entry


def compare_to_baseline(
    current: str,
    path: Path = _DEFAULT_PATH,
) -> BaselineComparison:
    if not is_valid(current):
        raise ValueError(f"Invalid cron expression: {current!r}")
    entry = _load(path)
    if entry is None:
        raise FileNotFoundError("No baseline has been set.")
    return BaselineComparison(
        baseline=entry.expression,
        current=current,
        changed=entry.expression != current,
        baseline_description=explain(entry.expression),
        current_description=explain(current),
    )


def clear_baseline(path: Path = _DEFAULT_PATH) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False
