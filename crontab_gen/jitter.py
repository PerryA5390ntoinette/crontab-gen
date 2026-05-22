"""Jitter analysis: detect whether a cron expression fires too predictably
and suggest randomised offset variants to spread load."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .expression import is_valid
from .next_run import next_runs


@dataclass
class JitterSuggestion:
    original: str
    variant: str
    description: str

    def __str__(self) -> str:
        return f"{self.variant}  # {self.description} (was: {self.original})"


@dataclass
class JitterResult:
    expression: str
    fires_per_hour: int
    predictable: bool
    suggestions: List[JitterSuggestion] = field(default_factory=list)

    def __str__(self) -> str:
        status = "predictable" if self.predictable else "already varied"
        lines = [
            f"expression : {self.expression}",
            f"fires/hour : {self.fires_per_hour}",
            f"status     : {status}",
        ]
        if self.suggestions:
            lines.append("suggestions:")
            for s in self.suggestions:
                lines.append(f"  {s}")
        return "\n".join(lines)


def _fires_per_hour(expression: str) -> int:
    """Count how many times the expression fires within a single hour."""
    runs = next_runs(expression, count=120)
    if not runs:
        return 0
    start = runs[0]
    return sum(1 for r in runs if (r - start).total_seconds() < 3600)


def _is_predictable(expression: str) -> bool:
    """Return True when the minute field is a simple wildcard or single value."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return False
    minute = parts[0]
    return minute == "*" or minute.isdigit()


def _build_suggestions(expression: str) -> List[JitterSuggestion]:
    parts = expression.strip().split()
    if len(parts) != 5:
        return []
    _, hour, dom, month, dow = parts
    suggestions = []
    for offset in (7, 13, 37, 53):
        variant = f"{offset} {hour} {dom} {month} {dow}"
        suggestions.append(
            JitterSuggestion(
                original=expression,
                variant=variant,
                description=f"shifted to minute {offset} to reduce thundering-herd",
            )
        )
    return suggestions


def analyse_jitter(expression: str) -> JitterResult:
    """Analyse an expression and return a JitterResult with load-spread suggestions."""
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")
    fph = _fires_per_hour(expression)
    predictable = _is_predictable(expression)
    suggestions = _build_suggestions(expression) if predictable else []
    return JitterResult(
        expression=expression,
        fires_per_hour=fph,
        predictable=predictable,
        suggestions=suggestions,
    )
