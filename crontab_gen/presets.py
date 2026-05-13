"""Common cron expression presets with descriptions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CronPreset:
    name: str
    expression: str
    description: str
    category: str
    alias: Optional[str] = None


PRESETS: list[CronPreset] = [
    CronPreset(
        name="every-minute",
        expression="* * * * *",
        description="Run every minute",
        category="frequent",
        alias="@always",
    ),
    CronPreset(
        name="hourly",
        expression="0 * * * *",
        description="Run once an hour at the beginning of the hour",
        category="frequent",
        alias="@hourly",
    ),
    CronPreset(
        name="daily",
        expression="0 0 * * *",
        description="Run once a day at midnight",
        category="daily",
        alias="@daily",
    ),
    CronPreset(
        name="daily-noon",
        expression="0 12 * * *",
        description="Run once a day at noon",
        category="daily",
    ),
    CronPreset(
        name="weekly",
        expression="0 0 * * 0",
        description="Run once a week at midnight on Sunday",
        category="weekly",
        alias="@weekly",
    ),
    CronPreset(
        name="monthly",
        expression="0 0 1 * *",
        description="Run once a month at midnight on the first day",
        category="monthly",
        alias="@monthly",
    ),
    CronPreset(
        name="yearly",
        expression="0 0 1 1 *",
        description="Run once a year at midnight on January 1st",
        category="yearly",
        alias="@yearly",
    ),
    CronPreset(
        name="weekdays",
        expression="0 9 * * 1-5",
        description="Run at 9am on every weekday (Monday through Friday)",
        category="weekly",
    ),
    CronPreset(
        name="every-5-minutes",
        expression="*/5 * * * *",
        description="Run every 5 minutes",
        category="frequent",
    ),
    CronPreset(
        name="every-15-minutes",
        expression="*/15 * * * *",
        description="Run every 15 minutes",
        category="frequent",
    ),
    CronPreset(
        name="every-30-minutes",
        expression="*/30 * * * *",
        description="Run every 30 minutes",
        category="frequent",
    ),
    CronPreset(
        name="midnight-weekdays",
        expression="0 0 * * 1-5",
        description="Run at midnight on weekdays only",
        category="weekly",
    ),
]


def get_preset(name: str) -> Optional[CronPreset]:
    """Look up a preset by name or alias."""
    name_lower = name.lower()
    for preset in PRESETS:
        if preset.name == name_lower or preset.alias == name_lower:
            return preset
    return None


def list_presets(category: Optional[str] = None) -> list[CronPreset]:
    """Return all presets, optionally filtered by category."""
    if category:
        return [p for p in PRESETS if p.category == category]
    return list(PRESETS)


def categories() -> list[str]:
    """Return all unique preset categories."""
    seen: set[str] = set()
    result = []
    for p in PRESETS:
        if p.category not in seen:
            seen.add(p.category)
            result.append(p.category)
    return result
