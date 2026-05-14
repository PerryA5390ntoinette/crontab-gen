"""Compare two cron expressions and produce a human-readable summary."""

from dataclasses import dataclass
from typing import List

from crontab_gen.expression import CronExpression, is_valid
from crontab_gen.explainer import explain


@dataclass
class FieldComparison:
    """Comparison result for a single cron field."""

    name: str
    left: str
    right: str
    same: bool

    def __str__(self) -> str:
        mark = "=" if self.same else "≠"
        return f"  {self.name:10s} {mark}  {self.left!r:20s}  {self.right!r}"


@dataclass
class CompareResult:
    """Full comparison between two cron expressions."""

    left: str
    right: str
    fields: List[FieldComparison]

    @property
    def identical(self) -> bool:
        return all(f.same for f in self.fields)

    @property
    def changed_fields(self) -> List[FieldComparison]:
        return [f for f in self.fields if not f.same]

    def __str__(self) -> str:
        lines = [
            f"Left : {self.left}",
            f"       {explain(self.left)}",
            f"Right: {self.right}",
            f"       {explain(self.right)}",
            "",
            f"{'Field':10s}    {'Left':20s}  Right",
            "-" * 50,
        ]
        for fc in self.fields:
            lines.append(str(fc))
        if self.identical:
            lines.append("\n✓ Expressions are identical.")
        else:
            lines.append(f"\n{len(self.changed_fields)} field(s) differ.")
        return "\n".join(lines)


FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]


def compare(left: str, right: str) -> CompareResult:
    """Compare two cron expressions field by field.

    Raises ValueError if either expression is invalid.
    """
    for expr in (left, right):
        if not is_valid(expr):
            raise ValueError(f"Invalid cron expression: {expr!r}")

    left_parts = left.split()
    right_parts = right.split()

    comparisons = [
        FieldComparison(
            name=name,
            left=lp,
            right=rp,
            same=(lp == rp),
        )
        for name, lp, rp in zip(FIELD_NAMES, left_parts, right_parts)
    ]

    return CompareResult(left=left, right=right, fields=comparisons)
