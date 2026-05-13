"""Compute the next N run times for a cron expression."""

from datetime import datetime, timedelta
from typing import List

from .expression import CronExpression, is_valid


def _matches_field(value: int, field_str: str, min_val: int, max_val: int) -> bool:
    """Return True if *value* satisfies the cron *field_str*."""
    if field_str == "*":
        return True

    for part in field_str.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if value == int(part):
                return True
    return False


def next_runs(expression: str, count: int = 5, after: datetime | None = None) -> List[datetime]:
    """Return the next *count* datetimes that match *expression*.

    Args:
        expression: A valid 5-field cron expression string.
        count:      How many future run times to return.
        after:      Start searching after this datetime (default: now).

    Returns:
        A list of naive :class:`datetime` objects (minute precision).

    Raises:
        ValueError: If *expression* is not valid.
    """
    if not is_valid(expression):
        raise ValueError(f"Invalid cron expression: {expression!r}")

    expr = CronExpression(expression)
    minute_f, hour_f, dom_f, month_f, dow_f = [
        f.value for f in expr.fields
    ]

    current = (after or datetime.now()).replace(second=0, microsecond=0)
    current += timedelta(minutes=1)  # start one minute ahead

    results: List[datetime] = []
    # Guard against infinite loops for pathological expressions
    limit = 60 * 24 * 366 * 4  # ~4 years of minutes
    steps = 0

    while len(results) < count and steps < limit:
        if (
            _matches_field(current.month, month_f, 1, 12)
            and _matches_field(current.day, dom_f, 1, 31)
            and _matches_field(current.weekday() + 1 if current.weekday() < 6 else 0, dow_f, 0, 7)
            and _matches_field(current.hour, hour_f, 0, 23)
            and _matches_field(current.minute, minute_f, 0, 59)
        ):
            results.append(current)
        current += timedelta(minutes=1)
        steps += 1

    return results
