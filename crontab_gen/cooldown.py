"""Cooldown checker: warns when two expressions fire too close together."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .next_run import next_runs
from .expression import is_valid


@dataclass
class CooldownWarning:
    expr_a: str
    expr_b: str
    gap_seconds: int
    min_seconds: int

    def __str__(self) -> str:
        return (
            f"Cooldown violation: '{self.expr_a}' and '{self.expr_b}' "
            f"fire only {self.gap_seconds}s apart (minimum {self.min_seconds}s)"
        )


@dataclass
class CooldownResult:
    warnings: List[CooldownWarning]

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.ok:
            return "OK: no cooldown violations detected"
        lines = ["Cooldown violations:"]
        for w in self.warnings:
            lines.append(f"  - {w}")
        return "\n".join(lines)


def check_cooldown(
    expressions: List[str],
    min_seconds: int = 60,
    lookahead: int = 5,
) -> CooldownResult:
    """Check whether any pair of expressions fires within *min_seconds* of each
    other over the next *lookahead* occurrences.

    Args:
        expressions: list of cron expression strings to compare pairwise.
        min_seconds: minimum allowed gap in seconds between firings.
        lookahead: how many upcoming run times to sample per expression.

    Returns:
        CooldownResult with any detected violations.
    """
    for expr in expressions:
        if not is_valid(expr):
            raise ValueError(f"Invalid cron expression: {expr!r}")

    warnings: List[CooldownWarning] = []
    run_times = [next_runs(expr, lookahead) for expr in expressions]

    for i in range(len(expressions)):
        for j in range(i + 1, len(expressions)):
            times_a = run_times[i]
            times_b = run_times[j]
            for ta in times_a:
                for tb in times_b:
                    gap = int(abs((ta - tb).total_seconds()))
                    if gap < min_seconds:
                        warnings.append(
                            CooldownWarning(
                                expr_a=expressions[i],
                                expr_b=expressions[j],
                                gap_seconds=gap,
                                min_seconds=min_seconds,
                            )
                        )
                        # one violation per pair is enough
                        break
                else:
                    continue
                break

    return CooldownResult(warnings=warnings)
