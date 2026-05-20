"""Status module: summarise the current state of stored cron data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_gen import (
    bookmark,
    favorite,
    history,
    note,
    snapshot,
    tags,
    template,
)


@dataclass
class StatusReport:
    """Aggregated counts of persisted cron artefacts."""

    bookmarks: int = 0
    favorites: int = 0
    history_entries: int = 0
    notes: int = 0
    snapshots: int = 0
    tags: int = 0
    templates: int = 0
    sections: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        lines = ["crontab-gen status", "-" * 20]
        pairs = [
            ("Bookmarks", self.bookmarks),
            ("Favorites", self.favorites),
            ("History entries", self.history_entries),
            ("Notes", self.notes),
            ("Snapshots", self.snapshots),
            ("Tags", self.tags),
            ("Templates", self.templates),
        ]
        for label, count in pairs:
            lines.append(f"  {label:<20} {count}")
        return "\n".join(lines)


def _safe_load(loader, path=None) -> list:
    """Call loader, returning an empty list on any error."""
    try:
        return loader(path) if path else loader()
    except Exception:  # noqa: BLE001
        return []


def build_status(
    *,
    bookmarks_path=None,
    favorites_path=None,
    history_path=None,
    notes_path=None,
    snapshots_path=None,
    tags_path=None,
    templates_path=None,
) -> StatusReport:
    """Build a :class:`StatusReport` by loading each data store."""
    return StatusReport(
        bookmarks=len(_safe_load(bookmark._load, bookmarks_path)),
        favorites=len(_safe_load(favorite._load, favorites_path)),
        history_entries=len(_safe_load(history._load, history_path)),
        notes=len(_safe_load(note._load, notes_path)),
        snapshots=len(_safe_load(snapshot._load, snapshots_path)),
        tags=len(_safe_load(tags._load, tags_path)),
        templates=len(_safe_load(template._load, templates_path)),
    )
