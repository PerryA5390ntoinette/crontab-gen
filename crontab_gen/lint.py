"""Lint cron expressions for common mistakes and suspicious patterns."""

from dataclasses import dataclass, field
from typing import List

from .expression import CronExpression, is_valid


@dataclass
class LintWarning:
    field: str
    message: str
    severity: str = "warning"  # "warning" | "info"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


@dataclass
class LintResult:
    expression: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return f"No issues found in '{self.expression}'."
        lines = [f"Lint results for '{self.expression}':"] + [
            f"  {w}" for w in self.warnings
        ]
        return "\n".join(lines)


def lint(expression: str) -> LintResult:
    """Analyse a cron expression and return a LintResult with warnings."""
    result = LintResult(expression=expression)

    if not is_valid(expression):
        result.warnings.append(
            LintWarning("expression", "Expression is not valid.", severity="warning")
        )
        return result

    expr = CronExpression(expression)
    minute, hour, dom, month, dow = (
        expr.fields["minute"],
        expr.fields["hour"],
        expr.fields["dom"],
        expr.fields["month"],
        expr.fields["dow"],
    )

    # Warn about */1 — equivalent to *
    for name, value in expr.fields.items():
        if value == "*/1":
            result.warnings.append(
                LintWarning(name, "'*/1' is redundant; use '*' instead.", severity="info")
            )

    # Warn if both DOM and DOW are restricted (non-*) — ambiguous union semantics
    if dom != "*" and dow != "*":
        result.warnings.append(
            LintWarning(
                "dom/dow",
                "Both day-of-month and day-of-week are restricted; "
                "cron uses OR logic which may be unintentional.",
                severity="warning",
            )
        )

    # Warn about high-frequency schedules (every minute)
    if minute == "*" and hour == "*":
        result.warnings.append(
            LintWarning(
                "minute/hour",
                "Expression runs every minute — ensure this is intentional.",
                severity="warning",
            )
        )

    # Warn about step value of 0 (invalid but sometimes entered)
    for name, value in expr.fields.items():
        if "/0" in value:
            result.warnings.append(
                LintWarning(name, "Step value of 0 is invalid.", severity="warning")
            )

    return result
