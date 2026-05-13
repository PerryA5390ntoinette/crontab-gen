"""Core cron expression parsing and validation module."""

from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int

    def is_valid(self) -> tuple[bool, Optional[str]]:
        """Validate a single cron field. Returns (valid, error_message)."""
        value = self.raw.strip()
        if value == "*":
            return True, None
        aliases = MONTH_ALIASES if self.name == "month" else (
            DOW_ALIASES if self.name == "day_of_week" else {}
        )
        try:
            parts = value.split(",")
            for part in parts:
                if "/" in part:
                    base, step = part.split("/", 1)
                    step_val = int(step)
                    if step_val <= 0:
                        return False, f"Step value must be positive in '{part}'"
                    if base != "*":
                        self._validate_range_or_value(base, aliases)
                elif "-" in part:
                    self._validate_range_or_value(part, aliases)
                else:
                    num = aliases.get(part.lower(), None)
                    if num is None:
                        num = int(part)
                    if not (self.min_val <= num <= self.max_val):
                        return False, f"Value {num} out of range [{self.min_val}-{self.max_val}]"
        except ValueError as e:
            return False, str(e)
        return True, None

    def _validate_range_or_value(self, part: str, aliases: dict):
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo_v = aliases.get(lo.lower(), int(lo))
            hi_v = aliases.get(hi.lower(), int(hi))
            if lo_v > hi_v:
                raise ValueError(f"Invalid range '{part}': start > end")
            for v in (lo_v, hi_v):
                if not (self.min_val <= v <= self.max_val):
                    raise ValueError(f"Value {v} out of range [{self.min_val}-{self.max_val}]")
        else:
            num = aliases.get(part.lower(), int(part))
            if not (self.min_val <= num <= self.max_val):
                raise ValueError(f"Value {num} out of range [{self.min_val}-{self.max_val}]")


@dataclass
class CronExpression:
    raw: str

    def fields(self) -> list[CronField]:
        parts = self.raw.strip().split()
        if len(parts) != 5:
            return []
        return [
            CronField(name=FIELD_NAMES[i], raw=parts[i],
                      min_val=FIELD_RANGES[FIELD_NAMES[i]][0],
                      max_val=FIELD_RANGES[FIELD_NAMES[i]][1])
            for i in range(5)
        ]

    def validate(self) -> tuple[bool, list[str]]:
        """Returns (is_valid, list_of_errors)."""
        parts = self.raw.strip().split()
        if len(parts) != 5:
            return False, [f"Expected 5 fields, got {len(parts)}"]
        errors = []
        for field in self.fields():
            valid, msg = field.is_valid()
            if not valid:
                errors.append(f"{field.name}: {msg}")
        return len(errors) == 0, errors
