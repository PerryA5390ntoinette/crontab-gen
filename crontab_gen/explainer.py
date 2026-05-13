"""Human-readable explanation generator for cron expressions."""

from crontab_gen.expression import CronExpression, MONTH_ALIASES, DOW_ALIASES

MONTH_NAMES = {v: k.capitalize() for k, v in MONTH_ALIASES.items()}
DOW_NAMES = {v: k.capitalize() for k, v in DOW_ALIASES.items()}
DOW_NAMES[7] = "Sun"  # 7 is also Sunday


def _explain_field(raw: str, unit: str, names: dict = None) -> str:
    value = raw.strip()
    if value == "*":
        return f"every {unit}"
    parts = value.split(",")
    descriptions = []
    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            base_desc = "every" if base == "*" else f"starting at {base}"
            descriptions.append(f"every {step} {unit}s ({base_desc})")
        elif "-" in part:
            lo, hi = part.split("-", 1)
            lo_label = names.get(int(lo), lo) if names else lo
            hi_label = names.get(int(hi), hi) if names else hi
            descriptions.append(f"{lo_label} through {hi_label}")
        else:
            try:
                num = int(part)
                label = names.get(num, str(num)) if names else str(num)
            except ValueError:
                label = part
            descriptions.append(label)
    return ", ".join(descriptions)


def explain(expression: str) -> str:
    """Return a human-readable explanation of a cron expression."""
    expr = CronExpression(expression)
    valid, errors = expr.validate()
    if not valid:
        return "Invalid expression:\n" + "\n".join(f"  - {e}" for e in errors)

    fields = expr.fields()
    minute = _explain_field(fields[0].raw, "minute")
    hour = _explain_field(fields[1].raw, "hour")
    dom = _explain_field(fields[2].raw, "day-of-month")
    month = _explain_field(fields[3].raw, "month", MONTH_NAMES)
    dow = _explain_field(fields[4].raw, "day-of-week", DOW_NAMES)

    parts = []
    if fields[0].raw == "*" and fields[1].raw == "*":
        parts.append("Every minute")
    elif fields[0].raw == "0" and fields[1].raw == "*":
        parts.append("At the start of every hour")
    else:
        parts.append(f"At {minute} past {hour}")

    if fields[2].raw != "*" or fields[3].raw != "*" or fields[4].raw != "*":
        time_parts = []
        if fields[3].raw != "*":
            time_parts.append(f"in {month}")
        if fields[2].raw != "*":
            time_parts.append(f"on day {dom} of the month")
        if fields[4].raw != "*":
            time_parts.append(f"on {dow}")
        parts.append(", ".join(time_parts))

    return ", ".join(filter(None, parts)) + "."
