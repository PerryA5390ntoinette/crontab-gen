"""Save and load named cron expression templates."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_TEMPLATE_FILE = os.path.expanduser("~/.crontab_gen_templates.json")


@dataclass
class TemplateEntry:
    name: str
    expression: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "description": self.description,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(data: Dict) -> "TemplateEntry":
        return TemplateEntry(
            name=data["name"],
            expression=data["expression"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def _load(path: str) -> Dict[str, TemplateEntry]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {k: TemplateEntry.from_dict(v) for k, v in raw.items()}


def _save(entries: Dict[str, TemplateEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({k: v.to_dict() for k, v in entries.items()}, fh, indent=2)


def save_template(
    name: str,
    expression: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    path: str = DEFAULT_TEMPLATE_FILE,
) -> TemplateEntry:
    entries = _load(path)
    entry = TemplateEntry(name=name, expression=expression, description=description, tags=tags or [])
    entries[name] = entry
    _save(entries, path)
    return entry


def get_template(name: str, path: str = DEFAULT_TEMPLATE_FILE) -> Optional[TemplateEntry]:
    return _load(path).get(name)


def list_templates(path: str = DEFAULT_TEMPLATE_FILE) -> List[TemplateEntry]:
    return list(_load(path).values())


def delete_template(name: str, path: str = DEFAULT_TEMPLATE_FILE) -> bool:
    entries = _load(path)
    if name not in entries:
        return False
    del entries[name]
    _save(entries, path)
    return True
