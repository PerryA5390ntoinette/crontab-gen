"""Compare two cron expressions and describe the differences."""

from dataclasses import dataclass
from typing import List

from .expression import CronExpression, CronField
from .explainer import _explain_field


@dataclass
class FieldDiff:
    field: CronField
    left: str
    right: str
    left_explanation: str
    right_explanation: str

    @property
    def changed(self) -> bool:
        return self.left != self.right


@dataclass
class ExpressionDiff:
    left: str
    right: str
    field_diffs: List[FieldDiff]

    @property
    def has_changes(self) -> bool:
        return any(d.changed for d in self.field_diffs)

    @property
    def changed_fields(self) -> List[FieldDiff]:
        return [d for d in self.field_diffs if d.changed]


def diff_expressions(left: str, right: str) -> ExpressionDiff:
    """Compare two cron expressions field by field.

    Raises ValueError if either expression is invalid.
    """
    left_expr = CronExpression(left)
    right_expr = CronExpression(right)

    if not left_expr.is_valid():
        raise ValueError(f"Invalid left expression: {left!r}")
    if not right_expr.is_valid():
        raise ValueError(f"Invalid right expression: {right!r}")

    left_parts = left.split()
    right_parts = right.split()

    field_diffs = []
    for i, field in enumerate(CronField):
        lv = left_parts[i]
        rv = right_parts[i]
        field_diffs.append(
            FieldDiff(
                field=field,
                left=lv,
                right=rv,
                left_explanation=_explain_field(field, lv),
                right_explanation=_explain_field(field, rv),
            )
        )

    return ExpressionDiff(left=left, right=right, field_diffs=field_diffs)
