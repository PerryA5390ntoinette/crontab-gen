"""Suggest cron expressions based on natural-language-like keywords."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Suggestion:
    expression: str
    description: str
    keywords: List[str]

    def __str__(self) -> str:
        return f"{self.expression:<20} {self.description}"


_SUGGESTIONS: List[Suggestion] = [
    Suggestion("* * * * *",       "Every minute",                  ["every minute", "always", "minutely"]),
    Suggestion("0 * * * *",       "Every hour",                    ["every hour", "hourly"]),
    Suggestion("0 0 * * *",       "Every day at midnight",         ["daily", "every day", "midnight"]),
    Suggestion("0 12 * * *",      "Every day at noon",             ["noon", "midday", "every day at noon"]),
    Suggestion("0 0 * * 0",       "Every Sunday at midnight",      ["weekly", "every week", "sunday"]),
    Suggestion("0 0 1 * *",       "First day of every month",      ["monthly", "every month", "first of month"]),
    Suggestion("0 0 1 1 *",       "First day of every year",       ["yearly", "annually", "every year", "new year"]),
    Suggestion("*/5 * * * *",     "Every 5 minutes",               ["every 5 minutes", "5 min", "5 minutes"]),
    Suggestion("*/15 * * * *",    "Every 15 minutes",              ["every 15 minutes", "quarter hour", "15 min"]),
    Suggestion("*/30 * * * *",    "Every 30 minutes",              ["every 30 minutes", "half hour", "30 min"]),
    Suggestion("0 9-17 * * 1-5",  "Every hour during business hours (Mon-Fri)", ["business hours", "work hours", "weekday"]),
    Suggestion("0 0 * * 1-5",     "Every weekday at midnight",     ["weekday", "monday to friday", "workday"]),
    Suggestion("0 6 * * *",       "Every day at 6 AM",             ["morning", "6am", "wake up"]),
    Suggestion("0 22 * * *",      "Every day at 10 PM",            ["night", "10pm", "evening"]),
    Suggestion("0 0 15 * *",      "15th of every month",           ["15th", "mid month", "middle of month"]),
]


def suggest(query: str, limit: int = 5) -> List[Suggestion]:
    """Return suggestions whose keywords match the query string."""
    if not query or not query.strip():
        return _SUGGESTIONS[:limit]

    q = query.lower().strip()
    scored: List[tuple[int, Suggestion]] = []

    for s in _SUGGESTIONS:
        score = 0
        for kw in s.keywords:
            if kw in q or q in kw:
                score += 2
            elif any(word in kw for word in q.split()):
                score += 1
        if s.description.lower().find(q) != -1:
            score += 1
        if score > 0:
            scored.append((score, s))

    scored.sort(key=lambda t: t[0], reverse=True)
    return [s for _, s in scored[:limit]]
