"""Schedule summary: convert a cron expression into a human-friendly
recurrence description (e.g. 'Every 5 minutes', 'Daily at 03:00')."""

from __future__ import annotations

from crontab_gen.expression import CronExpression, is_valid


class ScheduleSummary:
    """Holds the plain-English summary of a cron expression."""

    def __init__(self, expression: str, summary: str) -> None:
        self.expression = expression
        self.summary = summary

    def __str__(self) -> str:  # pragma: no cover
        return self.summary

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScheduleSummary({self.expression!r}, {self.summary!r})"


def _is_wildcard(value: str) -> bool:
    return value == "*"


def _is_step(value: str) -> bool:
    return value.startswith("*/")


def _step_value(value: str) -> int:
    return int(value.split("/")[1])


def summarise(expression: str) -> ScheduleSummary:
    """Return a :class:`ScheduleSummary` for *expression*.

    Raises ``ValueError`` if the expression is invalid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    expr = CronExpression(expression)
    minute, hour, dom, month, dow = (
        expr.fields["minute"],
        expr.fields["hour"],
        expr.fields["dom"],
        expr.fields["month"],
        expr.fields["dow"],
    )

    # Every minute
    if all(_is_wildcard(f) for f in (minute, hour, dom, month, dow)):
        return ScheduleSummary(expression, "Every minute")

    # Every N minutes
    if (
        _is_step(minute)
        and all(_is_wildcard(f) for f in (hour, dom, month, dow))
    ):
        n = _step_value(minute)
        return ScheduleSummary(expression, f"Every {n} minute{'s' if n != 1 else ''}")

    # Every hour at minute X
    if (
        not _is_wildcard(minute)
        and not _is_step(minute)
        and _is_wildcard(hour)
        and all(_is_wildcard(f) for f in (dom, month, dow))
    ):
        return ScheduleSummary(expression, f"Every hour at minute {minute}")

    # Daily at HH:MM
    if (
        not _is_wildcard(minute)
        and not _is_wildcard(hour)
        and not _is_step(minute)
        and not _is_step(hour)
        and all(_is_wildcard(f) for f in (dom, month, dow))
    ):
        hh = hour.zfill(2)
        mm = minute.zfill(2)
        return ScheduleSummary(expression, f"Daily at {hh}:{mm}")

    # Weekly on day X at HH:MM
    if (
        not _is_wildcard(dow)
        and not _is_wildcard(hour)
        and not _is_wildcard(minute)
        and all(_is_wildcard(f) for f in (dom, month))
    ):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_name = days[int(dow)] if dow.isdigit() and int(dow) < 7 else dow
        hh = hour.zfill(2)
        mm = minute.zfill(2)
        return ScheduleSummary(expression, f"Weekly on {day_name} at {hh}:{mm}")

    # Fallback
    return ScheduleSummary(expression, f"Custom schedule: {expression}")
