"""Retry policy advisor: suggest retry-safe cron expressions based on interval."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .expression import is_valid
from .explainer import explain


@dataclass
class RetryPolicy:
    """A suggested cron expression with retry metadata."""

    expression: str
    interval_minutes: int
    description: str
    jitter_note: str

    def __str__(self) -> str:
        return (
            f"{self.expression}  "
            f"(every {self.interval_minutes}m) — {self.description}"
        )


_BUILTIN_POLICIES: List[dict] = [
    {"expr": "* * * * *",   "interval": 1,    "jitter": "High contention; add jitter in your job runner."},
    {"expr": "*/2 * * * *", "interval": 2,    "jitter": "Suitable for fast retries with low risk."},
    {"expr": "*/5 * * * *", "interval": 5,    "jitter": "Good default for transient failure recovery."},
    {"expr": "*/10 * * * *","interval": 10,   "jitter": "Balanced retry cadence."},
    {"expr": "*/15 * * * *","interval": 15,   "jitter": "Use for moderate backoff strategies."},
    {"expr": "*/30 * * * *","interval": 30,   "jitter": "Half-hourly; good for non-critical retries."},
    {"expr": "0 * * * *",   "interval": 60,   "jitter": "Hourly retry; low frequency, high tolerance."},
    {"expr": "0 */2 * * *", "interval": 120,  "jitter": "Every 2 hours; suitable for slow external APIs."},
    {"expr": "0 */6 * * *", "interval": 360,  "jitter": "Quarter-day; for batch retry jobs."},
    {"expr": "0 0 * * *",   "interval": 1440, "jitter": "Daily retry; last-resort recovery."},
]


def suggest_retry_policies(
    max_interval_minutes: int = 1440,
    min_interval_minutes: int = 1,
) -> List[RetryPolicy]:
    """Return retry-safe cron expressions within the given interval bounds."""
    if min_interval_minutes < 1:
        raise ValueError("min_interval_minutes must be >= 1")
    if max_interval_minutes < min_interval_minutes:
        raise ValueError(
            "max_interval_minutes must be >= min_interval_minutes"
        )

    results: List[RetryPolicy] = []
    for policy in _BUILTIN_POLICIES:
        interval = policy["interval"]
        if min_interval_minutes <= interval <= max_interval_minutes:
            expr = policy["expr"]
            if not is_valid(expr):
                continue
            results.append(
                RetryPolicy(
                    expression=expr,
                    interval_minutes=interval,
                    description=explain(expr),
                    jitter_note=policy["jitter"],
                )
            )
    return results


def closest_retry_policy(target_minutes: int) -> Optional[RetryPolicy]:
    """Return the built-in retry policy whose interval is closest to *target_minutes*.

    If *target_minutes* is less than 1, a ``ValueError`` is raised.  Returns
    ``None`` only when ``_BUILTIN_POLICIES`` is empty (should not happen in
    normal usage).
    """
    if target_minutes < 1:
        raise ValueError("target_minutes must be >= 1")

    all_policies = suggest_retry_policies(
        min_interval_minutes=1, max_interval_minutes=1440
    )
    if not all_policies:
        return None

    return min(all_policies, key=lambda p: abs(p.interval_minutes - target_minutes))
